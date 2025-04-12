from collections.abc import AsyncGenerator, AsyncIterator

import pytest
from litestar import Litestar
from litestar.testing import AsyncTestClient
from pytest_databases.docker.postgres import PostgresService
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from src.app import app, db_config


app.debug = True


@pytest.fixture
async def engine(postgres_service: PostgresService) -> AsyncEngine:
    """Postgresql instance for end-to-end testing.

    Returns:
        Async SQLAlchemy engine instance.

    """
    return create_async_engine(
        URL(
            drivername="postgresql+psycopg",
            username=postgres_service.user,
            password=postgres_service.password,
            host=postgres_service.host,
            port=postgres_service.port,
            database=postgres_service.database,
            query={},  # type:ignore[arg-type]
        ),
        echo=False,
        poolclass=NullPool,
    )


@pytest.fixture(name="sessionmaker")
async def fx_session_maker_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(bind=engine, expire_on_commit=False)


@pytest.fixture(name="session")
async def fx_session(sessionmaker: async_sessionmaker[AsyncSession]) -> AsyncGenerator[AsyncSession, None]:
    async with sessionmaker() as session:
        yield session


@pytest.fixture(autouse=True)
def _patch_db(
    engine: AsyncEngine,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(db_config, "engine_instance", engine)


@pytest.fixture
async def test_client() -> AsyncIterator[AsyncTestClient[Litestar]]:
    async with AsyncTestClient(app=app) as client:
        yield client
