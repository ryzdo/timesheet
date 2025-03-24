import pytest
from litestar import get
from litestar.testing import AsyncTestClient
from pytest_databases.docker.postgres import PostgresService
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool

from src.app import db_config


pytestmark = pytest.mark.anyio


pytest_plugins = [
    "pytest_databases.docker.postgres",
]


@pytest.fixture(autouse=True)
def _patch_db(
    engine: AsyncEngine,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(db_config, "engine_instance", engine)


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


async def test_db_session_dependency(
    engine: AsyncEngine,
) -> None:
    """Test that handlers receive session attached to patched engine.

    Args:
        app: The test Litestar instance
        engine: The patched SQLAlchemy engine instance.

    """

    @get("/db-session-test")
    async def db_session_dependency_patched(db_session: AsyncSession) -> dict[str, str]:
        return {"result": f"{db_session.bind is engine = }"}

    from src.app import app

    app.register(db_session_dependency_patched)
    # can't use test client as it always starts its own event loop
    async with AsyncTestClient(app) as client:
        response = await client.get("/db-session-test")
        assert response.json()["result"] == "db_session.bind is engine = True"
