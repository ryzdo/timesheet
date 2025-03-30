import pytest
from litestar import get
from litestar.testing import AsyncTestClient
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession


pytestmark = pytest.mark.anyio


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
