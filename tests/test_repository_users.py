import pytest
from unittest.mock import AsyncMock
from src.database.models import User
from src.repository.users import UserRepository
from src.schemas.users import UserCreate


@pytest.fixture
def mock_session():
    return AsyncMock()


@pytest.fixture
def user_repo(mock_session):
    return UserRepository(mock_session)


@pytest.fixture
def test_user():
    return User(
        id=1,
        username="testuser",
        email="test@example.com",
        hashed_password="hashed123",
        avatar="default.jpg",
        confirmed=False,
    )


@pytest.mark.asyncio
async def test_get_user_by_id(user_repo, mock_session, test_user):
    mock_session.execute.return_value.scalar_one_or_none.return_value = test_user
    result = await user_repo.get_user_by_id(user_id=1)
    assert result == test_user


@pytest.mark.asyncio
async def test_get_user_by_username(user_repo, mock_session, test_user):
    mock_session.execute.return_value.scalar_one_or_none.return_value = test_user
    result = await user_repo.get_user_by_username(username="testuser")
    assert result == test_user


@pytest.mark.asyncio
async def test_get_user_by_email(test_db, test_user):
    """
    Тестує отримання користувача за email.
    """
    user_repo = UserRepository(test_db)
    user = await user_repo.get_user_by_email(test_user.email)
    assert user is not None
    assert user.email == test_user.email


@pytest.mark.asyncio
async def test_create_user(user_repo, mock_session):
    user_data = UserCreate(
        username="newuser", email="new@example.com", password="password123"
    )
    mock_session.commit.return_value = None
    result = await user_repo.create_user(user_data, avatar="avatar.jpg")
    assert result.username == "newuser"
    assert result.email == "new@example.com"
    assert result.avatar == "avatar.jpg"


@pytest.mark.asyncio
async def test_confirmed_email(test_db, test_user):
    """
    Тестує підтвердження email користувача.
    """
    user_repo = UserRepository(test_db)
    await user_repo.confirmed_email(test_user.email)
    confirmed_user = await user_repo.get_user_by_email(test_user.email)
    assert confirmed_user.confirmed is True


@pytest.mark.asyncio
async def test_update_avatar_url(user_repo, mock_session, test_user):
    mock_session.execute.return_value.scalar_one_or_none.return_value = test_user
    result = await user_repo.update_avatar_url(
        email="test@example.com", url="new_avatar.jpg"
    )
    assert result.avatar == "new_avatar.jpg"
    mock_session.commit.assert_called_once()
