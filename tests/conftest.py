import asyncio
import pytest
import pytest_asyncio
import sys
import os
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + "/../"))
from main import app
from src.database.models import Base, User
from src.database.db import get_db
from src.services.auth import create_access_token, Hash


SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, expire_on_commit=False, bind=engine
)

test_user = {
    "username": "deadpool",
    "email": "deadpool@example.com",
    "password": "12345678",
}


@pytest_asyncio.fixture(scope="module")
def event_loop():
    """Create an event loop for the entire module."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="module")
async def init_models():
    """Ensure database is set up before tests"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with TestingSessionLocal() as session:
        hash_password = Hash().get_password_hash(test_user["password"])
        current_user = User(
            username=test_user["username"],
            email=test_user["email"],
            hashed_password=hash_password,
            confirmed=True,  # Mark as confirmed to avoid authentication issues
            avatar="<https://twitter.com/gravatar>",
            created_at=datetime.utcnow(),
        )
        session.add(current_user)
        await session.commit()


@pytest.fixture(scope="module")
def client():
    """Override the database dependency in FastAPI"""

    async def override_get_db():
        async with TestingSessionLocal() as session:
            try:
                yield session
            finally:
                await session.close()

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


@pytest_asyncio.fixture(scope="module")
async def get_token():
    """Generate a valid authentication token"""
    return await create_access_token(data={"sub": test_user["username"]})


@pytest.fixture(scope="module")
def get_token(client):
    response = client.post(
        "api/auth/register",
        json={"email": "test@example.com", "password": "testpassword"},
    )
    assert response.status_code == 201, response.text

    response = client.post(
        "api/auth/login", json={"email": "test@example.com", "password": "testpassword"}
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    """Ініціалізуємо тестову БД перед запуском тестів"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session():
    """Надає сесію для тестів"""
    async with AsyncSession(engine) as session:
        yield session


@pytest.fixture(scope="module")
async def test_db():
    async with async_sessionmaker(bind=engine)() as session:
        yield session
