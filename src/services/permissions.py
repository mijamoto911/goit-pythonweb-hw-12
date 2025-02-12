from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models import User, UserRole
from src.database.db import get_db
from src.services.auth import get_current_user


def is_admin(user: User = Depends(get_current_user)):
    """Перевіряє, чи є користувач адміністратором"""
    if user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Недостатньо прав"
        )
    return user
