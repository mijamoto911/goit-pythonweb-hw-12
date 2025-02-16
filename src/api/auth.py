"""
Цей модуль містить маршрути автентифікації для API.

Включає:
- Реєстрацію користувача
- Вхід користувача
- Запит підтвердження email
- Підтвердження email
- Оновлення аватару користувача
"""

from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    status,
    BackgroundTasks,
    Request,
    UploadFile,
    File,
)
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm

from src.schemas.users import UserCreate, Token, User, RequestEmail, UserResponse
from src.services.auth import (
    create_access_token,
    Hash,
    get_email_from_token,
    get_current_user,
    create_reset_token,
    verify_reset_token,
)
from src.services.users import UserService
from src.services.upload_file import UploadFileService
from src.database.db import get_db
from src.services.email import send_email, send_reset_email
from src.conf.config import settings
from src.conf import messages
from pydantic import BaseModel, EmailStr
from src.database.models import User

router = APIRouter(prefix="/auth", tags=["auth"])


class ResetPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordConfirm(BaseModel):
    token: str
    new_password: str


router.post("/request-password-reset")


async def request_password_reset(
    data: ResetPasswordRequest, db: AsyncSession = Depends(get_db)
):
    """Обробка запиту на скидання пароля"""
    user = await db.execute(User.select().where(User.email == data.email))
    user = user.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="Користувач не знайдений")

    token = create_reset_token(user.email)
    await send_reset_email(user.email, token)

    return {"message": "Лист для скидання пароля відправлено"}


@router.post("/reset-password")
async def reset_password(
    data: ResetPasswordConfirm, db: AsyncSession = Depends(get_db)
):
    """Зміна пароля після підтвердження"""
    email = verify_reset_token(data.token)
    if not email:
        raise HTTPException(
            status_code=400, detail="Недійсний або протермінований токен"
        )

    user = await db.execute(User.select().where(User.email == email))
    user = user.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="Користувач не знайдений")

    user.hashed_password = Hash.hash_password(data.new_password)
    await db.commit()

    return {"message": "Пароль успішно змінено"}


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register_user(
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Реєстрація нового користувача.

    Перевіряє, чи існує користувач із таким email або username.
    Якщо користувач не існує, створює нового і відправляє email з підтвердженням.

    :param user_data: Данні нового користувача.
    :param background_tasks: Фонова задача для відправлення email.
    :param request: Об'єкт запиту для отримання базового URL.
    :param db: Сесія бази даних.
    :return: Створений користувач.
    """
    user_service = UserService(db)

    email_user = await user_service.get_user_by_email(user_data.email)
    if email_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=messages.USER_ALREADY_EXIST,
        )

    username_user = await user_service.get_user_by_username(user_data.username)
    if username_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=messages.USERNAME_ALREADY_EXIST,
        )

    user_data.password = Hash().get_password_hash(user_data.password)
    new_user = await user_service.create_user(user_data)

    background_tasks.add_task(
        send_email, new_user.email, new_user.username, request.base_url
    )

    return new_user


@router.post("/login", response_model=Token)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    Вхід користувача в систему.

    Перевіряє правильність email та пароля, а також чи підтверджений email.

    :param form_data: Данні для авторизації (email та пароль).
    :param db: Сесія бази даних.
    :return: Токен доступу.
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_username(form_data.username)

    if user and not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=messages.USER_NOT_AUTHENTICATED,
        )

    if not user or not Hash().verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=messages.WRONG_PASSWORD,
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=messages.USER_EMAIL_NOT_CONFIRMED,
        )

    access_token = await create_access_token(data={"sub": user.username})

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/request_email", response_model=UserResponse)
async def request_email(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Запит на повторне підтвердження email.

    :param body: Данні запиту (email).
    :param background_tasks: Фонова задача для відправки email.
    :param request: Об'єкт запиту для отримання базового URL.
    :param db: Сесія бази даних.
    :return: Повідомлення про підтвердження email.
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.email)

    if user.confirmed:
        return {"message": "Ваша електронна пошта вже підтверджена"}

    if user:
        background_tasks.add_task(
            send_email, user.email, user.username, request.base_url
        )

    return {"message": "Перевірте свою електронну пошту для підтвердження"}


@router.get("/confirmed_email/{token}", response_model=UserResponse)
async def confirmed_email(
    token: str,
    db: Session = Depends(get_db),
):
    """
    Підтвердження електронної пошти.

    :param token: Токен підтвердження.
    :param db: Сесія бази даних.
    :return: Повідомлення про статус підтвердження.
    """
    email = await get_email_from_token(token)
    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error"
        )

    if user.confirmed:
        return {"message": "Ваша електронна пошта вже підтверджена"}

    await user_service.confirmed_email(email)

    return {"message": "Електронну пошту підтверджено"}


@router.patch("/avatar", response_model=UserResponse)
async def update_avatar_user(
    file: UploadFile = File(),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Оновлення аватару користувача.

    :param file: Завантажений файл.
    :param user: Поточний користувач.
    :param db: Сесія бази даних.
    :return: Оновлений користувач.
    """
    avatar_url = UploadFileService(
        settings.CLD_NAME, settings.CLD_API_KEY, settings.CLD_API_SECRET
    ).upload_file(file, user.username)

    user_service = UserService(db)
    user = await user_service.update_avatar_url(user.email, avatar_url)

    return user
