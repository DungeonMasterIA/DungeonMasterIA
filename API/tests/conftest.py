import os
from collections.abc import AsyncGenerator

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["SECRET_KEY"] = "test-secret-key-at-least-32-bytes-long"

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.core.db import Base, get_async_db_session
from main import app

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
async def db_engine():
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def client(db_engine) -> AsyncGenerator[AsyncClient, None]:
    session_maker = async_sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async def override_get_async_db_session() -> AsyncGenerator[AsyncSession, None]:
        async with session_maker() as session:
            yield session

    app.dependency_overrides[get_async_db_session] = override_get_async_db_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as test_client:
        yield test_client

    app.dependency_overrides.clear()
