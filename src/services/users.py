from sqlalchemy.ext.asyncio import AsyncSession
from libgravatar import Gravatar

from src.repository.users import UserRepository
from src.schemas.users import UserCreate


class UserService:
    """
    Сервіс для управління користувачами.

    :param db: Асинхронна сесія SQLAlchemy.
    :type db: AsyncSession
    """

    def __init__(self, db: AsyncSession):
        """
        Ініціалізує сервіс із базою даних.

        :param db: Асинхронна сесія SQLAlchemy.
        """
        self.repository = UserRepository(db)

    async def create_user(self, body: UserCreate):
        """
        Створює нового користувача.

        :param body: Об'єкт зі схемою даних для створення користувача.
        :type body: UserCreate
        :return: Створений користувач.
        :rtype: User
        """
        avatar = None
        try:
            g = Gravatar(body.email)
            avatar = g.get_image()
        except Exception as e:
            print(e)

        return await self.repository.create_user(body, avatar)

    async def get_user_by_id(self, user_id: int):
        """
        Отримує користувача за його ідентифікатором.

        :param user_id: Ідентифікатор користувача.
        :type user_id: int
        :return: Об'єкт користувача або None.
        :rtype: User | None
        """
        return await self.repository.get_user_by_id(user_id)

    async def get_user_by_username(self, username: str):
        """
        Отримує користувача за його ім'ям користувача.

        :param username: Ім'я користувача.
        :type username: str
        :return: Об'єкт користувача або None.
        :rtype: User | None
        """
        return await self.repository.get_user_by_username(username)

    async def get_user_by_email(self, email: str):
        """
        Отримує користувача за його email.

        :param email: Email користувача.
        :type email: str
        :return: Об'єкт користувача або None.
        :rtype: User | None
        """
        return await self.repository.get_user_by_email(email)

    async def confirmed_email(self, email: str):
        """
        Підтверджує email користувача.

        :param email: Email користувача.
        :type email: str
        :return: None
        """
        return await self.repository.confirmed_email(email)
