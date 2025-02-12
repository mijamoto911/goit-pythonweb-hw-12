from datetime import datetime, date

from sqlalchemy import Column, Integer, String, Boolean, func, Table, Enum
from sqlalchemy.orm import relationship, mapped_column, Mapped, DeclarativeBase
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import Date, DateTime
from sqlalchemy.ext.declarative import declarative_base
import enum

Base = declarative_base()


class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"


class Base(DeclarativeBase):
    """
    Базовий клас для моделей SQLAlchemy.

    Додає поля створення (`created_at`) і оновлення (`updated_at`), які автоматично
    заповнюються під час операцій у базі даних.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )
    """Час створення запису."""

    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )
    """Час останнього оновлення запису."""


class Contact(Base):
    """
    Модель представлення контакту в базі даних.

    :param id: Унікальний ідентифікатор контакту.
    :type id: int
    :param first_name: Ім'я контакту.
    :type first_name: str
    :param last_name: Прізвище контакту.
    :type last_name: str
    :param email: Електронна пошта контакту.
    :type email: str
    :param phone_number: Номер телефону контакту.
    :type phone_number: str
    :param birthday: Дата народження контакту.
    :type birthday: date
    :param additional_data: Додаткова інформація про контакт.
    :type additional_data: str
    :param user_id: Ідентифікатор користувача, якому належить контакт.
    :type user_id: int
    """

    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    """Унікальний ідентифікатор контакту."""

    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    """Ім'я контакту."""

    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    """Прізвище контакту."""

    email: Mapped[str] = mapped_column(String(100), nullable=False)
    """Електронна пошта контакту."""

    phone_number: Mapped[str] = mapped_column(String(100), nullable=False)
    """Номер телефону контакту."""

    birthday: Mapped[date] = mapped_column(Date, nullable=False)
    """Дата народження контакту."""

    additional_data: Mapped[str] = mapped_column(String(150), nullable=False)
    """Додаткова інформація про контакт."""

    user_id = Column(
        "user_id", ForeignKey("users.id", ondelete="CASCADE"), default=None
    )
    """Зовнішній ключ для прив'язки контакту до користувача."""

    user = relationship("User", backref="contacts")
    """Зв'язок з користувачем (One-to-Many)."""


class User(Base):
    """
    Модель представлення користувача в базі даних.

    :param id: Унікальний ідентифікатор користувача.
    :type id: int
    :param username: Унікальне ім'я користувача.
    :type username: str
    :param email: Електронна пошта користувача.
    :type email: str
    :param hashed_password: Хешований пароль користувача.
    :type hashed_password: str
    :param avatar: URL зображення аватара користувача.
    :type avatar: str, optional
    :param confirmed: Чи підтверджений обліковий запис користувача.
    :type confirmed: bool, default=False
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    """Унікальний ідентифікатор користувача."""

    username = Column(String, unique=True, nullable=False)
    """Унікальне ім'я користувача."""

    email = Column(String, unique=True, nullable=False)
    """Електронна пошта користувача."""

    hashed_password = Column(String, nullable=False)
    """Хешований пароль користувача."""

    avatar = Column(String(255), nullable=True)
    """URL зображення аватара користувача."""

    confirmed = Column(Boolean, default=False)
    """Прапорець, що вказує на підтвердження облікового запису."""
    is_active = Column(Boolean, default=True)

    role = Column(Enum(UserRole), default=UserRole.USER)
