from datetime import datetime, date
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict, EmailStr, field_validator


class ContactBase(BaseModel):
    """
    Базова модель для контактів.
    """

    first_name: str = Field(
        max_length=50, min_length=2, description="Ім'я контакту (від 2 до 50 символів)."
    )
    last_name: str = Field(
        max_length=50,
        min_length=2,
        description="Прізвище контакту (від 2 до 50 символів).",
    )
    email: EmailStr = Field(description="Електронна пошта контакту.")
    phone_number: str = Field(
        max_length=20,
        min_length=6,
        description="Номер телефону (від 6 до 20 символів).",
    )
    birthday: date = Field(description="Дата народження контакту.")
    additional_data: Optional[str] = Field(
        max_length=150,
        description="Додаткова інформація про контакт (макс. 150 символів).",
    )

    @field_validator("birthday")
    def validate_birthday(cls, v):
        """
        Валідація дня народження: не може бути у майбутньому.

        :param v: Введена дата.
        :return: Перевірена дата.
        :raises ValueError: Якщо дата народження у майбутньому.
        """
        if v > date.today():
            raise ValueError("Birthday cannot be in the future")
        return v


class ContactResponse(ContactBase):
    """
    Відповідь сервера при отриманні інформації про контакт.
    """

    id: int = Field(description="Унікальний ідентифікатор контакту.")
    created_at: datetime | None = Field(description="Дата створення запису.")
    updated_at: Optional[datetime] | None = Field(
        description="Дата останнього оновлення запису."
    )
    model_config = ConfigDict(from_attributes=True)


class ContactBirthdayRequest(BaseModel):
    """
    Запит на отримання контактів з майбутнім днем народження.
    """

    days: int = Field(
        ge=0, le=366, description="Кількість днів наперед для пошуку (від 0 до 366)."
    )
