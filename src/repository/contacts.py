from typing import List
from sqlalchemy import select, or_, func, extract, and_, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from datetime import timedelta
from src.database.models import Contact, User
from src.schemas.contacts import ContactBase, ContactResponse


class ContactRepository:
    """
    Репозиторій для управління контактами користувача.
    """

    def __init__(self, session: AsyncSession):
        """
        Ініціалізація репозиторію.

        :param session: Асинхронна сесія бази даних.
        """
        self.db = session

    async def get_contact(self, contact_id: int, user: User) -> Contact | None:
        stmt = select(Contact).filter_by(id=contact_id, user=user)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_contacts(self, skip: int, limit: int, user: User) -> List[Contact]:
        """
        Отримати список контактів користувача.

        :param skip: Кількість контактів, які потрібно пропустити.
        :param limit: Максимальна кількість контактів у відповіді.
        :param user: Об'єкт користувача, для якого отримуються контакти.
        :return: Список об'єктів Contact.
        """
        stmt = select(Contact).filter_by(user=user).offset(skip).limit(limit)
        contacts = await self.db.execute(stmt)
        return (await contacts.scalars()).all()

    async def get_contact_by_id(self, contact_id: int, user: User) -> Contact | None:
        """
        Отримати контакт за його ID.

        :param contact_id: Ідентифікатор контакту.
        :param user: Об'єкт користувача, якому належить контакт.
        :return: Об'єкт Contact або None, якщо контакт не знайдено.
        """
        stmt = select(Contact).filter_by(id=contact_id, user=user)
        contact = await self.db.execute(stmt)
        return contact.scalar_one_or_none()

    async def create_contact(
        self, body: ContactBase, user: User, tags: List[str]
    ) -> Contact:
        """
        Створити новий контакт.

        :param body: Дані контакту.
        :param user: Об'єкт користувача, якому належатиме контакт.
        :param tags: Список міток для контакту.
        :return: Створений об'єкт Contact.
        """
        contact = Contact(**body.model_dump(exclude_unset=True), user=user)
        self.db.add(contact)
        await self.db.commit()
        await self.db.refresh(contact)
        return contact

    async def remove_contact(self, contact_id: int, user: User) -> Contact | None:
        """
        Видалити контакт за його ID.

        :param contact_id: Ідентифікатор контакту.
        :param user: Об'єкт користувача, якому належить контакт.
        :return: Видалений об'єкт Contact або None, якщо контакт не знайдено.
        """
        contact = await self.get_contact_by_id(contact_id, user)
        if contact:
            await self.db.delete(contact)
            await self.db.commit()
        return contact

    async def update_contact(
        self, contact_id: int, data: dict, user: User
    ) -> Contact | None:
        """
        Оновити контакт.

        :param contact_id: Ідентифікатор контакту.
        :param body: Нові дані контакту.
        :param user: Об'єкт користувача, якому належить контакт.
        :return: Оновлений об'єкт Contact або None, якщо контакт не знайдено.
        """
        contact = await self.get_contact(contact_id, user)
        if not contact:
            return None

        for key, value in data.items():
            setattr(contact, key, value)
        await self.db.commit()
        return contact

    async def search_contacts(
        self, search: str, skip: int, limit: int, user: User
    ) -> List[Contact]:
        """
        Виконати пошук контактів за ім'ям, email або іншими параметрами.

        :param search: Рядок для пошуку.
        :param skip: Кількість контактів, які потрібно пропустити.
        :param limit: Максимальна кількість контактів у відповіді.
        :param user: Об'єкт користувача, для якого виконується пошук.
        :return: Список знайдених контактів.
        """
        stmt = (
            select(Contact)
            .filter(
                or_(Contact.first_name, Contact.last_name).ilike(f"%{search}%"),
                Contact.email.ilike(f"%{search}%"),
                Contact.phone_number.ilike(f"%{search}%"),
                Contact.birthday.ilike(f"%{search}%"),
                Contact.additional_data.ilike(f"%{search}%"),
            )
            .filter_by(user=user)
            .offset(skip)
            .limit(limit)
        )
        contacts = await self.db.execute(stmt)
        return contacts.scalars().all()
