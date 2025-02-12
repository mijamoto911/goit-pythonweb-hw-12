from pydantic import ConfigDict
from pydantic_settings import BaseSettings
from pathlib import Path
from dotenv import load_dotenv
import os

# Завантаження змінних оточення з файлу .env
load_dotenv()


class Settings(BaseSettings):
    """
    Клас для збереження конфігураційних налаштувань застосунку.

    Налаштування завантажуються з файлу `.env` або передаються через змінні оточення.

    :param DB_URL: URL підключення до бази даних.
    :type DB_URL: str
    :param JWT_SECRET: Секретний ключ для підпису JWT-токенів.
    :type JWT_SECRET: str
    :param JWT_ALGORITHM: Алгоритм хешування для JWT-токенів (за замовчуванням `"HS256"`).
    :type JWT_ALGORITHM: str
    :param JWT_EXPIRATION_SECONDS: Термін дії JWT-токена у секундах (за замовчуванням `3600`).
    :type JWT_EXPIRATION_SECONDS: int
    :param MAIL_USERNAME: Логін для поштового сервера.
    :type MAIL_USERNAME: str
    :param MAIL_PASSWORD: Пароль для поштового сервера.
    :type MAIL_PASSWORD: str
    :param MAIL_FROM: Адреса відправника електронної пошти.
    :type MAIL_FROM: str
    :param MAIL_PORT: Порт для підключення до поштового сервера.
    :type MAIL_PORT: int
    :param MAIL_SERVER: Адреса поштового сервера.
    :type MAIL_SERVER: str
    :param MAIL_FROM_NAME: Ім'я відправника.
    :type MAIL_FROM_NAME: str
    :param MAIL_STARTTLS: Чи використовувати `STARTTLS` для безпечного з'єднання.
    :type MAIL_STARTTLS: bool, default=False
    :param MAIL_SSL_TLS: Чи використовувати `SSL/TLS` для безпечного з'єднання.
    :type MAIL_SSL_TLS: bool, default=True
    :param USE_CREDENTIALS: Чи використовувати автентифікацію для пошти.
    :type USE_CREDENTIALS: bool, default=True
    :param VALIDATE_CERTS: Чи перевіряти сертифікати поштового сервера.
    :type VALIDATE_CERTS: bool, default=True
    :param TEMPLATE_FOLDER: Шлях до папки з email-шаблонами.
    :type TEMPLATE_FOLDER: Path
    :param CLD_NAME: Назва акаунту в Cloudinary.
    :type CLD_NAME: str
    :param CLD_API_KEY: API-ключ для Cloudinary.
    :type CLD_API_KEY: int
    :param CLD_API_SECRET: Секретний ключ API для Cloudinary.
    :type CLD_API_SECRET: str
    """

    DB_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_SECONDS: int = 3600
    APP_URL: str = os.getenv("APP_URL", "http://localhost:8000")

    DATABASE_URL: str = os.getenv("DB_URL", os.getenv("DATABASE_URL"))

    REDIS_URL: str = os.getenv("REDIS_URL")
    SECRET_KEY: str = os.getenv("SECRET_KEY")

    SMTP_HOST: str = os.getenv("SMTP_HOST")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", 587))
    SMTP_USER: str = os.getenv("SMTP_USER")
    SMTP_PASS: str = os.getenv("SMTP_PASS")

    CLOUD_NAME: str = os.getenv("CLOUD_NAME")
    CLOUD_API_KEY: str = os.getenv("CLOUD_API_KEY")
    CLOUD_API_SECRET: str = os.getenv("CLOUD_API_SECRET")
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_FROM_NAME: str
    MAIL_STARTTLS: bool = False
    MAIL_SSL_TLS: bool = True
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True
    TEMPLATE_FOLDER: Path = Path(__file__).parent.parent / "services" / "templates"

    CLD_NAME: str
    CLD_API_KEY: int = 326488457974591
    CLD_API_SECRET: str = "secret"

    model_config = ConfigDict(
        extra="ignore", env_file=".env", env_file_encoding="utf-8", case_sensitive=True
    )

    class Config:
        env_file = ".env"

    """Конфігурація моделі: ігнорує зайві змінні оточення, завантажує `.env`, враховує регістр."""


# Ініціалізація налаштувань
settings = Settings()
"""
Об'єкт `settings`, що містить всі конфігураційні налаштування застосунку.
"""
