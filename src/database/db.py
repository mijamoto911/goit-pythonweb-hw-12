import contextlib
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
    AsyncSession,
)

from src.conf.config import settings

DATABASE_URL = settings.DATABASE_URL

engine = create_async_engine(DATABASE_URL, future=True, echo=True)
SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)


class DatabaseSessionManager:
    """
    Менеджер сесій бази даних для роботи з SQLAlchemy у асинхронному режимі.

    :param url: URL підключення до бази даних.
    :type url: str
    """

    def __init__(self, url: str):
        """
        Ініціалізація менеджера сесій бази даних.

        :param url: URL підключення до бази даних.
        :type url: str
        """
        self._engine: AsyncEngine | None = create_async_engine(url)
        self._session_maker: async_sessionmaker = async_sessionmaker(
            autoflush=False, autocommit=False, bind=self._engine
        )

    @contextlib.asynccontextmanager
    async def session(self):
        """
        Контекстний менеджер для створення та керування сесією бази даних.

        :raises Exception: Якщо сесія не ініціалізована.
        :raises SQLAlchemyError: Якщо під час виконання виникає помилка SQLAlchemy.
        :yield: Об'єкт асинхронної сесії бази даних.
        :rtype: AsyncSession
        """
        if self._session_maker is None:
            raise Exception("Database session is not initialized")
        session = self._session_maker()
        try:
            yield session
        except SQLAlchemyError as e:
            await session.rollback()
            raise  # Повторне викликання помилки SQLAlchemy
        finally:
            await session.close()


# Ініціалізація глобального екземпляра менеджера сесій
sessionmanager = DatabaseSessionManager(settings.DB_URL)


async def get_db():
    """
    Генератор для отримання асинхронної сесії бази даних.

    :yield: Об'єкт сесії бази даних.
    :rtype: AsyncSession
    """
    async with sessionmanager.session() as session:
        yield session
