"""
Цей модуль містить API-ендпоінти для управління користувачами.

Функціональність:
- Отримання інформації про поточного користувача.
"""

from fastapi import APIRouter, Depends, Request, HTTPException
from src.services.limiter import limiter
from src.schemas.users import User
from src.services.auth import get_current_user
from src.services.redis_cache import redis_cache
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.db import get_db
from src.database.models import User, UserRole
from src.repository.users import UserRepository
from src.services.permissions import is_admin
from pydantic import BaseModel, EmailStr

router = APIRouter(prefix="/users", tags=["users"])


class RoleUpdateRequest(BaseModel):
    email: EmailStr
    new_role: UserRole


@router.put("/change-role")
async def change_user_role(
    request: RoleUpdateRequest,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(is_admin),
):
    """Змінює роль користувача (тільки для адміністраторів)"""
    user = await db.execute(User.select().where(User.email == request.email))
    user = user.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="Користувач не знайдений")

    user.role = request.new_role
    await db.commit()
    return {"message": f"Роль користувача {user.email} змінено на {user.role}"}


@router.get("/me", response_model=User)
@limiter.limit("10/minute")
async def me(request: Request, user: User = Depends(get_current_user)):
    """
    Отримання інформації про поточного користувача.

    **Rate Limit:** 10 запитів на хвилину.

    :param request: Об'єкт HTTP-запиту.
    :param user: Поточний користувач (авторизований).
    :return: Об'єкт користувача.
    """
    return user


@router.get("/users/{user_id}")
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    cache_key = f"user:{user_id}"
    cached_user = await redis_cache.get(cache_key)

    if cached_user:
        return cached_user
    user = await UserRepository(db).get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    await redis_cache.set(cache_key, user.dict(), expire=600)
    return user


@router.put("/users/{user_id}")
async def update_user(
    user_id: int, update_data: dict, db: AsyncSession = Depends(get_db)
):
    user = await UserRepository(db).update_user(user_id, update_data)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    cache_key = f"user:{user_id}"
    await redis_cache.set(cache_key, user.dict(), expire=600)

    return user


@router.delete("/users/{user_id}")
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    success = await UserRepository(db).delete_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")

    cache_key = f"user:{user_id}"
    await redis_cache.delete(cache_key)

    return {"message": "User deleted"}
