import asyncio
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from datetime import datetime

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
def auth_client(client):
    response = client.post("api/auth/register", json=test_user)
    assert response.status_code == 201, response.text
    response = client.post(
        "api/auth/login",
        json={
            "email": test_user.get("email"),
            "password": test_user.get("password"),
        },
    )
    assert response.status_code == 200, response.text
    token = response.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client
