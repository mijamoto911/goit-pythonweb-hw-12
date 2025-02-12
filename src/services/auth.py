from datetime import datetime, timedelta, UTC
from typing import Optional
import os
from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from fastapi.security import (
    OAuth2PasswordBearer,
    HTTPBearer,
    HTTPAuthorizationCredentials,
)
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from src.database.db import get_db
from src.conf.config import settings
from src.services.users import UserService

SECRET_KEY = os.getenv("SECRET_KEY", "supersecret")
ALGORITHM = "HS256"


class Hash:
    """
    Клас для хешування паролів та перевірки їхньої коректності.
    """

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Перевіряє, чи збігається введений пароль із хешованим.

        :param plain_password: Введений користувачем пароль.
        :param hashed_password: Захешований пароль із бази даних.
        :return: True, якщо паролі збігаються, інакше False.
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """
        Генерує хеш пароля.

        :param password: Пароль користувача.
        :return: Захешований пароль.
        """
        return self.pwd_context.hash(password)


oauth2_scheme = HTTPBearer()


async def create_access_token(data: dict, expires_delta: Optional[int] = None) -> str:
    """
    Створює новий JWT-токен доступу.

    :param data: Дані, які будуть включені в токен.
    :param expires_delta: Час у секундах до закінчення дії токена (необов’язково).
    :return: Закодований JWT-токен.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + timedelta(seconds=expires_delta)
    else:
        expire = datetime.now(UTC) + timedelta(seconds=settings.JWT_EXPIRATION_SECONDS)
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
    token = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token


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


def create_reset_token(email: str):
    """Генерує токен для скидання пароля (дійсний 1 годину)"""
    expiration = datetime.utcnow() + timedelta(hours=1)
    to_encode = {"sub": email, "exp": expiration}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_reset_token(token: str):
    """Перевіряє токен та повертає email"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None
