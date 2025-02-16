from datetime import datetime, timedelta, UTC
from typing import Optional
import os
from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from src.database.db import get_db
from src.conf.config import settings
from src.services.users import UserService


class Hash:
    """
    Клас для хешування паролів та перевірки їхньої коректності.
    """

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @classmethod
    def hash_password(cls, password: str) -> str:
        """Генерує хеш пароля"""
        return cls.pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Перевіряє, чи збігається введений пароль із хешованим"""
        return Hash.pwd_context.verify(plain_password, hashed_password)


oauth2_scheme = HTTPBearer()


async def create_access_token(data: dict, expires_delta: Optional[int] = None) -> str:
    """
    Створює новий JWT-токен доступу.

    :param data: Дані, які будуть включені в токен.
    :param expires_delta: Час у секундах до закінчення дії токена (необов’язково).
    :return: Закодований JWT-токен.
    """
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(
        seconds=expires_delta or settings.JWT_EXPIRATION_SECONDS
    )
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


async def get_current_user(
    token: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    """
    Отримує поточного автентифікованого користувача з токена.

    :param token: JWT-токен авторизації.
    :param db: Сесія бази даних.
    :return: Об'єкт користувача, якщо він автентифікований.
    :raises HTTPException: Якщо токен недійсний або користувача не знайдено.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token.credentials, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user_service = UserService(db)
    user = await user_service.get_user_by_username(username)
    if user is None:
        raise credentials_exception
    return user


def create_email_token(data: dict) -> str:
    """
    Створює JWT-токен для підтвердження електронної пошти.

    :param data: Дані для кодування в токен.
    :return: Закодований JWT-токен.
    """
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(days=7)
    to_encode.update({"iat": datetime.now(UTC), "exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


async def get_email_from_token(token: str) -> str:
    """
    Отримує електронну пошту з токена підтвердження.

    :param token: JWT-токен підтвердження.
    :return: Електронна пошта користувача.
    :raises HTTPException: Якщо токен недійсний.
    """
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        email = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Неправильний токен для перевірки електронної пошти",
            )
        return email
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Неправильний токен для перевірки електронної пошти",
        )


def create_reset_token(email: str) -> str:
    """
    Генерує токен для скидання пароля (дійсний 1 годину)

    :param email: Електронна пошта користувача.
    :return: JWT-токен для скидання пароля.
    """
    expiration = datetime.now(UTC) + timedelta(hours=1)
    to_encode = {"sub": email, "exp": expiration}
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def verify_reset_token(token: str) -> Optional[str]:
    """
    Перевіряє токен скидання пароля та повертає email, якщо токен валідний.

    :param token: JWT-токен скидання пароля.
    :return: Email користувача або None, якщо токен недійсний.
    """
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        return payload.get("sub")
    except JWTError:
        return None
