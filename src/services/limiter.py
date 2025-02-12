from fastapi import APIRouter, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from src.schemas.users import User

# Ініціалізація маршрутизатора для користувачів
router = APIRouter(prefix="/users", tags=["users"])

# Обмежувач запитів (Rate Limiting)
limiter = Limiter(key_func=get_remote_address)


@router.get("/me", response_model=User)
@limiter.limit("5/minute")
async def my_endpoint(request: Request):
    """
    Отримання інформації про поточного користувача.

    :param request: Запит FastAPI.
    :type request: Request

    :return: JSON-відповідь із повідомленням.
    :rtype: dict
    :raise HTTPException: У разі перевищення ліміту запитів.
    """
    return {"message": "It is my route"}
