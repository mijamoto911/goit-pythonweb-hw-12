import pytest
from unittest.mock import AsyncMock
from datetime import date
from src.database.models import Contact, User
from src.repository.contacts import ContactRepository
from src.schemas.contacts import ContactBase


@pytest.fixture
def mock_session():
    return AsyncMock()


@pytest.fixture
def contact_repo(mock_session):
    return ContactRepository(mock_session)


@pytest.fixture
def test_user():
    return User(id=1, username="testuser", email="test@example.com")


@pytest.fixture
def test_contact(test_user):
    return Contact(
        id=1,
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        phone_number="123456789",
        birthday=date(1990, 1, 1),
        additional_data="Some data",
        user=test_user,
    )


@pytest.mark.asyncio
async def test_get_contacts(contact_repo, mock_session, test_user):
    mock_session.execute.return_value.scalars.return_value.all.return_value = [
        "contact1",
        "contact2",
    ]
    result = await contact_repo.get_contacts(skip=0, limit=10, user=test_user)
    assert len(result) == 2


@pytest.mark.asyncio
async def test_get_contact_by_id(test_db, test_user, test_contact):
    """
    Тестує отримання контакту за ID.
    """
    contact_repo = ContactRepository(test_db)
    contact = await contact_repo.get_contact(test_contact.id, test_user)
    assert contact is not None
    assert contact.id == test_contact.id


@pytest.mark.asyncio
async def test_create_contact(contact_repo, mock_session, test_user):
    contact_data = ContactBase(
        first_name="Jane",
        last_name="Doe",
        email="jane@example.com",
        phone_number="987654321",
        birthday=date(1995, 5, 5),
        additional_data="Extra info",
    )
    mock_session.commit.return_value = None
    result = await contact_repo.create_contact(contact_data, user=test_user, tags=[])
    assert result.first_name == "Jane"
    assert result.email == "jane@example.com"


@pytest.mark.asyncio
async def test_update_contact(test_db, test_user, test_contact):
    """
    Тестує оновлення контакту.
    """
    contact_repo = ContactRepository(test_db)
    updated_contact = await contact_repo.update_contact(
        test_contact.id, {"first_name": "UpdatedName"}, test_user
    )
    assert updated_contact.first_name == "UpdatedName"


@pytest.mark.asyncio
async def test_delete_contact(test_db, test_user, test_contact):
    """
    Тестує видалення контакту.
    """
    contact_repo = ContactRepository(test_db)
    result = await contact_repo.remove_contact(test_contact.id, test_user)
    assert result is True


@pytest.mark.asyncio
async def test_remove_contact(contact_repo, mock_session, test_user, test_contact):
    mock_session.execute.return_value.scalar_one_or_none.return_value = test_contact
    result = await contact_repo.remove_contact(contact_id=1, user=test_user)
    assert result == test_contact
    mock_session.delete.assert_called_once_with(test_contact)
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_search_contacts(test_db, test_user, test_contact):
    """
    Тестує пошук контактів.
    """
    contact_repo = ContactRepository(test_db)
    results = await contact_repo.search_contacts(
        test_contact.first_name, 0, 10, test_user
    )
    assert len(results) > 0
    assert test_contact in results
