"""
Цей модуль містить утилітарні API-ендпоінти, зокрема healthchecker.

Функціональність:
- Перевірка стану бази даних.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from src.database.db import get_db
from src.conf import messages

router = APIRouter(tags=["utils"])


@router.get("/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_db)):
    """
    Перевіряє стан підключення до бази даних.

    **Процес перевірки:**
    - Виконується SQL-запит `SELECT 1`.
    - Якщо відповідь відсутня — повертається помилка 500.
    - Якщо відповідь є — повертається повідомлення про працездатність додатку.

    :param db: Асинхронна сесія підключення до БД.
    :return: JSON-повідомлення про стан підключення до БД.
    :raises HTTPException 500: Якщо БД не налаштована або підключення не вдалось.
    """
    try:
        result = await db.execute(text("SELECT 1"))
        result = result.scalar_one_or_none()

        if result is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database is not configured correctly",
            )
        return {"message": messages.APP_IS_HEALTHY}
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error connecting to the database",
        )
