import asyncio
from collections.abc import AsyncGenerator, Generator
from typing import Literal

import asyncpg
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from alembic import command
from alembic.config import Config
from app.db.uow import DBUnitOfWork
from app.settings import settings


def run_migrations(mode: Literal["upgrade", "downgrade"] = "upgrade") -> None:
    """Run migrations.

    Args:
        mode: The mode to run the migrations in.

    """
    cfg = Config("alembic.ini")
    if mode == "upgrade":
        command.upgrade(cfg, "head")
    else:
        command.downgrade(cfg, "base")


@pytest.fixture(scope="session", autouse=True)
def setup_test_db() -> Generator[None]:
    """Set up a test database."""

    async def _create_db() -> None:
        """Create a test database."""
        admin_url = (
            f"postgresql://{settings.db_username}:{settings.db_password}@{settings.db_host}:{settings.db_port}/postgres"
        )
        conn = await asyncpg.connect(dsn=admin_url)
        exists = await conn.fetchval("SELECT 1 FROM pg_database WHERE datname = $1", settings.db_name)
        if not exists:
            await conn.execute(f'CREATE DATABASE "{settings.db_name}"')
        await conn.close()

    asyncio.run(_create_db())

    run_migrations(mode="upgrade")
    yield
    run_migrations(mode="downgrade")


@pytest_asyncio.fixture(scope="session")
async def test_engine() -> AsyncGenerator[create_async_engine]:
    """Create a test engine.

    Yields:
        create_async_engine: a test engine.

    """
    engine = create_async_engine(settings.db_url, echo=True, pool_pre_ping=True, pool_size=5, max_overflow=10)
    try:
        yield engine
    finally:
        await engine.dispose()


@pytest_asyncio.fixture
async def test_async_sessionmaker(  # noqa: RUF029
    test_engine: create_async_engine,
) -> AsyncGenerator[async_sessionmaker]:
    """Create a test session factory.

    Yields:
        async_sessionmaker: a session factory.

    """
    sessionmaker_ = async_sessionmaker(bind=test_engine, expire_on_commit=False, autoflush=False)
    yield sessionmaker_


@pytest_asyncio.fixture
async def test_uow(test_async_sessionmaker: async_sessionmaker) -> AsyncGenerator[DBUnitOfWork]:
    """Create a test unit of work.

    Yields:
        DBUnitOfWork: a DBUnitOfWork instance.

    """
    async with DBUnitOfWork(test_async_sessionmaker) as uow:
        yield uow
