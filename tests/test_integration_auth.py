from unittest.mock import Mock

import pytest
from sqlalchemy import select
from src.conf import messages
from src.services.users import UserService
from src.database.models import User
from tests.conftest import TestingSessionLocal, auth_client

user_data = {
    "username": "agent007",
    "email": "agent007@gmail.com",
    "password": "12345678",
}


def test_signup(auth_client, monkeypatch):
    """✅ Ensure a new user can sign up."""
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_email", mock_send_email)

    response = auth_client.post("/api/auth/register", json=user_data)
    assert response.status_code in [
        201,
        409,
    ], response.text  # ✅ Handle user already exists
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert "hashed_password" not in data
    assert "avatar" in data


@pytest.mark.asyncio
async def test_repeat_signup(auth_client, monkeypatch):
    """✅ Ensure duplicate signup fails."""
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_email", mock_send_email)

    response = auth_client.post("/api/auth/register", json=user_data)
    assert response.status_code == 409, response.text
    data = response.json()
    assert data["detail"] == messages.USER_ALREADY_EXIST


def test_not_confirmed_login(auth_client):

    response = auth_client.post(
        "api/auth/login",
        json={
            "email": user_data.get("email"),
            "password": user_data.get("password"),
        },
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == messages.USER_EMAIL_NOT_CONFIRMED


@pytest.mark.asyncio
async def test_login(auth_client):
    async with TestingSessionLocal() as session:
        current_user = await session.execute(
            select(User).where(User.email == user_data.get("email"))
        )
        current_user = current_user.scalar_one_or_none()
        if current_user:
            current_user.confirmed = True
            await session.commit()

    response = auth_client.post(
        "/api/auth/login",
        json={"email": user_data["email"], "password": user_data["password"]},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer", f'token_type should be {data["token_type"]}'


def test_wrong_password_login(auth_client):
    response = auth_client.post(
        "api/auth/login",
        json={"email": user_data.get("email"), "password": "password is wrong"},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == messages.WRONG_PASSWORD


def test_wrong_username_login(auth_client):
    response = auth_client.post(
        "api/auth/login",
        json={"email": "wrong email", "password": user_data.get("password")},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == messages.WRONG_PASSWORD


def test_validation_error_login(auth_client):
    response = auth_client.post(
        "api/auth/login", json={"password": user_data.get("password")}
    )
    assert response.status_code == 422, response.text
    data = response.json()
    assert "detail" in data
