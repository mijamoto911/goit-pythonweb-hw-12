from pathlib import Path
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr
from src.services.auth import create_email_token
from src.conf.config import settings
import smtplib

# Конфігурація підключення до поштового сервера
conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=settings.USE_CREDENTIALS,
    VALIDATE_CERTS=settings.VALIDATE_CERTS,
    TEMPLATE_FOLDER=Path(__file__).parent / "templates",
)


async def send_email(email: EmailStr, username: str, host: str):
    """
    Відправляє email для підтвердження реєстрації користувача.

    :param email: Email-адреса отримувача.
    :param username: Ім'я користувача.
    :param host: Доменне ім'я або IP сервера.

    :raises ConnectionErrors: Виникає у разі проблем з підключенням до поштового сервера.
    """
    try:
        token_verification = create_email_token({"sub": email})
        message = MessageSchema(
            subject="Confirm your email",
            recipients=[email],
            template_body={
                "host": host,
                "username": username,
                "token": token_verification,
            },
            subtype=MessageType.html,
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="verify_email.html")
        print(f"✅ Лист на підтвердження email надіслано: {email}")

    except ConnectionErrors as err:
        print(f"❌ Помилка підключення до поштового сервера: {err}")
    except smtplib.SMTPException as smtp_err:
        print(f"❌ SMTP-помилка: {smtp_err}")
    except Exception as e:
        print(f"❌ Несподівана помилка: {e}")


async def send_reset_email(email: str, token: str):
    """
    Відправляє email для скидання пароля.

    :param email: Email користувача.
    :param token: Унікальний токен для скидання пароля.

    :raises ConnectionErrors: Виникає у разі проблем з поштовим сервером.
    """
    try:
        reset_link = (
            f"{settings.APP_URL}/reset-password?token={token}"  # APP_URL з .env
        )
        message = MessageSchema(
            subject="Скидання пароля",
            recipients=[email],
            body=f"Для скидання пароля перейдіть за посиланням: <a href='{reset_link}'>Скинути пароль</a>",
            subtype="html",
        )

        fm = FastMail(conf)
        await fm.send_message(message)
        print(f"✅ Лист для скидання пароля надіслано: {email}")

    except ConnectionErrors as err:
        print(f"❌ Помилка підключення до поштового сервера: {err}")
    except smtplib.SMTPException as smtp_err:
        print(f"❌ SMTP-помилка: {smtp_err}")
    except Exception as e:
        print(f"❌ Несподівана помилка: {e}")
