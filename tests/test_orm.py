from collections.abc import Generator
from datetime import datetime

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, clear_mappers, sessionmaker

from src.filling.adapters.orm import mapper_registry, start_mappers
from src.filling.domain import model
from src.filling.domain.enums import EmploymentCode


@pytest.fixture
def session() -> Generator[Session]:
    engine = create_engine("sqlite:///:memory:")
    mapper_registry.metadata.create_all(engine)
    start_mappers()
    yield sessionmaker(bind=engine)()
    clear_mappers()


def test_saving_employment_hours(session: Session) -> None:
    eh = model.EmploymentHours(EmploymentCode.DAY_SHIFT, 8)
    session.add(eh)
    session.commit()

    rows = list(session.execute(text('SELECT * FROM "employment_hours"')))
    assert rows == [("DAY_SHIFT", 8)]


def test_saving_employment_day(session: Session) -> None:
    ed = model.EmploymentDay(datetime.fromisoformat("2025-01-31"))
    session.add(ed)
    session.commit()
    rows = list(session.execute(text('SELECT * FROM "employment_days"')))
    assert rows == [("2025-01-31")]
