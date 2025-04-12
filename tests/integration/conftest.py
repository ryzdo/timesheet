from collections.abc import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, clear_mappers, sessionmaker

from src.filling.adapters.orm import mapper_registry, start_mappers


@pytest.fixture
def session(session_factory: sessionmaker[Session]) -> Session:
    return session_factory()


@pytest.fixture
def session_factory() -> Generator[sessionmaker[Session]]:
    engine = create_engine("sqlite:///:memory:")
    mapper_registry.metadata.create_all(engine)
    start_mappers()
    yield sessionmaker(bind=engine)
    clear_mappers()
