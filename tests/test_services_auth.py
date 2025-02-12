import pytest
from unittest.mock import AsyncMock
from src.services.auth import create_access_token, Hash, get_email_from_token
from datetime import timedelta
from jose import jwt
from src.conf.config import settings


@pytest.fixture
def test_data():
    return {"sub": "testuser@example.com"}


@pytest.fixture
def test_token(test_data):
    return create_access_token(test_data, expires_delta=3600)


def test_create_access_token():
    """
    Тестує створення токена доступу.
    """
    token = create_access_token({"sub": "testuser"})
    assert isinstance(token, str)


def test_verify_password():
    hashed = Hash().get_password_hash("mypassword")
    assert Hash().verify_password("mypassword", hashed) is True


@pytest.mark.asyncio
async def test_get_email_from_token():
    """
    Тестує отримання email з токена.
    """
    token = create_access_token({"sub": "user@example.com"})
    email = await get_email_from_token(token)
    assert email == "user@example.com"


def test_get_email_from_token():
    token = create_access_token({"sub": "test@example.com"})
    email = get_email_from_token(token)
    assert email == "test@example.com"
