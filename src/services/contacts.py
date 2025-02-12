from sqlalchemy.ext.asyncio import AsyncSession

from src.repository.contacts import ContactRepository
from src.database.models import User
from src.schemas.contacts import ContactResponse, ContactBase


class ContactService:
    """
    Сервісний клас для управління контактами користувачів.

    Використовується для створення, отримання, оновлення та видалення контактів.
    """

    def __init__(self, db: AsyncSession):
        """
        Ініціалізує сервіс контактів із переданою сесією бази даних.

        :param db: Асинхронна сесія бази даних.
        """
        self.contact_repository = ContactRepository(db)

    async def create_contact(self, body: ContactBase, user: User):
        """
        Створює новий контакт для користувача.

        :param body: Дані нового контакту.
        :param user: Користувач, якому належить контакт.
        :return: Створений об'єкт контакту.
        """
        return await self.contact_repository.create_contact(body, user=user, tags=[])

    async def get_contacts(self, skip: int, limit: int, user: User):
        """
        Отримує список контактів користувача з можливістю пагінації.

        :param skip: Кількість пропущених записів (offset).
        :param limit: Максимальна кількість записів для отримання.
        :param user: Користувач, чиї контакти потрібно отримати.
        :return: Список об'єктів контактів.
        """
        return await self.contact_repository.get_contacts(skip, limit, user)

    async def get_contact(self, contact_id: int, user: User):
        """
        Отримує контакт за його ID.

        :param contact_id: Унікальний ідентифікатор контакту.
        :param user: Користувач, якому належить контакт.
        :return: Об'єкт контакту або None, якщо не знайдено.
        """
        return await self.contact_repository.get_contact_by_id(contact_id, user)

    async def update_contact(self, contact_id: int, body: ContactBase, user: User):
        """
        Оновлює інформацію про контакт.

        :param contact_id: Унікальний ідентифікатор контакту.
        :param body: Оновлені дані контакту.
        :param user: Користувач, якому належить контакт.
        :return: Оновлений об'єкт контакту або None, якщо не знайдено.
        """
        return await self.contact_repository.update_contact(contact_id, body, user)

    async def remove_contact(self, contact_id: int, user: User):
        """
        Видаляє контакт за його ID.

        :param contact_id: Унікальний ідентифікатор контакту.
        :param user: Користувач, якому належить контакт.
        :return: Видалений об'єкт контакту або None, якщо не знайдено.
        """
        return await self.contact_repository.remove_contact(contact_id, user)

    async def search_contacts(self, text: str, skip: int, limit: int, user: User):
        """
        Виконує пошук контактів за ім'ям, прізвищем, email або іншими полями.

        :param text: Текст пошуку.
        :param skip: Кількість пропущених записів (offset).
        :param limit: Максимальна кількість записів для отримання.
        :param user: Користувач, у якого здійснюється пошук.
        :return: Список знайдених контактів.
        """
        return await self.contact_repository.search_contacts(text, skip, limit, user)

    async def upcoming_birthdays(self, days: int, user: User):
        """
        Отримує список контактів, які мають день народження протягом заданої кількості днів.

        :param days: Кількість днів для перевірки майбутніх днів народження.
        :param user: Користувач, у якого здійснюється пошук.
        :return: Список контактів із майбутніми днями народження.
        """
        return await self.contact_repository.upcoming_birthdays(days, user)
