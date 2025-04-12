import pytest


pytest_plugins = [
    "pytest_databases.docker.postgres",
]


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"
