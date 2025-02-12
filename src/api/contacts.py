"""
Цей модуль містить API-ендпоінти для управління контактами.

Функціональність:
- Отримання списку контактів
- Отримання інформації про окремий контакт
- Створення нового контакту
- Оновлення контакту
- Видалення контакту
- Пошук контактів
- Отримання контактів з найближчими днями народження
"""

from typing import List

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.database.models import User, Contact
from src.schemas.contacts import ContactBase, ContactResponse, ContactBirthdayRequest
from src.services.contacts import ContactService
from src.services.auth import get_current_user
from src.conf import messages
from src.services.permissions import is_admin

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get("/", response_model=List[ContactResponse], status_code=status.HTTP_200_OK)
async def read_contacts(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Отримання списку контактів.

    :param skip: Кількість контактів, які потрібно пропустити.
    :param limit: Максимальна кількість контактів у відповіді.
    :param db: Сесія бази даних.
    :param user: Поточний користувач.
    :return: Список контактів.
    """
    contact_service = ContactService(db)
    contacts = await contact_service.get_contacts(skip, limit, user)
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse)
async def read_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Отримання інформації про конкретний контакт.

    :param contact_id: ID контакту.
    :param db: Сесія бази даних.
    :param user: Поточний користувач.
    :return: Контакт або помилка 404, якщо контакт не знайдено.
    """
    contact_service = ContactService(db)
    contact = await contact_service.get_contact(contact_id, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.CONTACT_NOT_FOUND
        )
    return contact


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(
    body: ContactBase,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Створення нового контакту.

    :param body: Дані нового контакту.
    :param db: Сесія бази даних.
    :param user: Поточний користувач.
    :return: Створений контакт.
    """
    contact_service = ContactService(db)
    return await contact_service.create_contact(body, user)


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    body: ContactBase,
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Оновлення контакту.

    :param body: Оновлені дані контакту.
    :param contact_id: ID контакту.
    :param db: Сесія бази даних.
    :param user: Поточний користувач.
    :return: Оновлений контакт або помилка 404, якщо контакт не знайдено.
    """
    contact_service = ContactService(db)
    contact = await contact_service.update_contact(contact_id, body, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.CONTACT_NOT_FOUND
        )
    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Видалення контакту.

    :param contact_id: ID контакту.
    :param db: Сесія бази даних.
    :param user: Поточний користувач.
    :return: Порожня відповідь або помилка 404, якщо контакт не знайдено.
    """
    contact_service = ContactService(db)
    contact = await contact_service.remove_contact(contact_id, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.CONTACT_NOT_FOUND
        )
    return


@router.get("/search/", response_model=List[ContactResponse])
async def search_contacts(
    text: str,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Пошук контактів за ім'ям, email або іншими полями.

    :param text: Текст для пошуку.
    :param skip: Кількість контактів, які потрібно пропустити.
    :param limit: Максимальна кількість контактів у відповіді.
    :param db: Сесія бази даних.
    :param user: Поточний користувач.
    :return: Список контактів, які відповідають критеріям пошуку.
    """
    contact_service = ContactService(db)
    contacts = await contact_service.search_contacts(text, skip, limit, user)
    return contacts


@router.post("/upcoming-birthdays", response_model=List[ContactResponse])
async def upcoming_birthdays(
    body: ContactBirthdayRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Отримання списку контактів з найближчими днями народження.

    :param body: Кількість днів для пошуку найближчих днів народження.
    :param db: Сесія бази даних.
    :param user: Поточний користувач.
    :return: Список контактів, у яких день народження у вказаний період.
    """
    contact_service = ContactService(db)
    contacts = await contact_service.upcoming_birthdays(body.days, user)
    return contacts


@router.get("/all")
async def get_all_contacts(
    db: AsyncSession = Depends(get_db), admin: User = Depends(is_admin)
):
    """Дозволяє лише адміністратору отримати всі контакти"""
    contacts = await db.execute(Contact.select())
    return contacts.scalars().all()
