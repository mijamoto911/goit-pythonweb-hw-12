from datetime import datetime, date
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict, EmailStr, field_validator


class User(BaseModel):
    """
    Модель користувача для відповіді API.
    """

    id: int = Field(description="Унікальний ідентифікатор користувача.")
    username: str = Field(description="Ім'я користувача.")
    email: str = Field(description="Електронна пошта користувача.")
    avatar: str = Field(description="URL аватару користувача.")

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    """
    Модель для створення нового користувача.
    """

    username: str = Field(description="Ім'я користувача.")
    email: str = Field(description="Електронна пошта користувача.")
    password: str = Field(description="Пароль користувача.")


class Token(BaseModel):
    """
    Модель для відповіді сервера після успішної авторизації.
    """

    access_token: str = Field(description="JWT токен доступу.")
    token_type: str = Field(description="Тип токену (наприклад, 'Bearer').")


class UserLogin(BaseModel):
    """
    Модель для авторизації користувача.
    """

    email: str = Field(description="Електронна пошта користувача.")
    password: str = Field(description="Пароль користувача.")


class RequestEmail(BaseModel):
    """
    Модель для запиту на відновлення пароля або підтвердження електронної пошти.
    """

    email: EmailStr = Field(description="Електронна пошта користувача.")


from pydantic import BaseModel, EmailStr


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    avatar: str | None = None
    confirmed: bool

    class Config:
        from_attributes = True


class UserRead(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True
