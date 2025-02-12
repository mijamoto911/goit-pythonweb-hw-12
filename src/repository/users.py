from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User
from src.schemas.users import UserCreate


class UserRepository:
    """
    Репозиторій для управління користувачами.
    """

    def __init__(self, session: AsyncSession):
        """
        Ініціалізація репозиторію.

        :param session: Асинхронна сесія бази даних.
        """
        self.db = session

    async def get_user_by_id(self, user_id: int) -> User | None:
        """
        Отримати користувача за його ID.

        :param user_id: Ідентифікатор користувача.
        :return: Об'єкт User або None, якщо користувача не знайдено.
        """
        stmt = select(User).filter_by(id=user_id)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def get_user_by_username(self, username: str) -> User | None:
        """
        Отримати користувача за його ім'ям.

        :param username: Ім'я користувача.
        :return: Об'єкт User або None, якщо користувача не знайдено.
        """
        stmt = select(User).filter_by(username=username)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> User | None:
        """
        Отримати користувача за email.

        :param email: Email користувача.
        :return: Об'єкт User або None, якщо користувача не знайдено.
        """
        stmt = select(User).filter_by(email=email)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def create_user(self, body: UserCreate, avatar: str = None) -> User:
        """
        Створити нового користувача.

        :param body: Дані користувача.
        :param avatar: URL аватару користувача (необов'язковий параметр).
        :return: Створений об'єкт User.
        """
        user = User(
            **body.model_dump(exclude_unset=True, exclude={"password"}),
            hashed_password=body.password,
            avatar=avatar
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def confirmed_email(self, email: str) -> None:
        """
        Підтвердити email користувача.

        :param email: Email користувача.
        """
        user = await self.get_user_by_email(email)
        user.confirmed = True
        await self.db.commit()

    async def update_avatar_url(self, email: str, url: str) -> User:
        """
        Оновити URL аватару користувача.

        :param email: Email користувача.
        :param url: Новий URL аватару.
        :return: Оновлений об'єкт User.
        """
        user = await self.get_user_by_email(email)
        user.avatar = url
        await self.db.commit()
        await self.db.refresh(user)
        return user
