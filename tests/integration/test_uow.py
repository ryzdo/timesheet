from collections.abc import Sequence
from datetime import datetime

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session, sessionmaker

from src.filling.domain import model
from src.filling.domain.enums import EmploymentCode
from src.filling.service_layer import unit_of_work


def insert_work_day(session: Session, date: str) -> int:
    session.execute(
        text("INSERT INTO work_days (date) VALUES (:date)"),
        {"date": date},
    )
    work_day_id: int
    [[work_day_id]] = session.execute(
        text("SELECT id FROM work_days WHERE date=:date"),
        {"date": date},
    )
    return work_day_id


def get_added_work_times(session: Session, date: str) -> Sequence[str]:
    [wtimes] = session.execute(
        text("SELECT code, hours FROM work_times JOIN work_days AS wd ON work_day_id = wd.id WHERE date=:date"),
        {"date": date},
    )
    return wtimes


def test_uow_can_retrieve(session_factory: sessionmaker[Session]) -> None:
    session = session_factory()
    insert_work_day(session, "2025-01-31")
    session.commit()

    uow = unit_of_work.SqlAlchemyUnitOfWork(session_factory)
    with uow:
        wday = uow.work_days.get(date=datetime.fromisoformat("2025-01-31").date())
        wtime = model.WorkTime(EmploymentCode.DAY_HOUR, 3)
        assert wday is not None
        wday.add_work_time(wtime)
        uow.commit()

    getted_wtime = get_added_work_times(session, "2025-01-31")
    assert getted_wtime == ("DAY_HOUR", 3.0)


def test_rolls_back_uncommitted_work_by_default(session_factory: sessionmaker[Session]) -> None:
    uow = unit_of_work.SqlAlchemyUnitOfWork(session_factory)
    with uow:
        insert_work_day(uow.session, "2025-01-31")
    new_session = session_factory()
    rows = list(new_session.execute(text('SELECT * FROM "work_days"')))
    assert rows == []


def test_rolls_back_on_error(session_factory: sessionmaker[Session]) -> None:
    class MyExceptionError(Exception):
        pass

    uow = unit_of_work.SqlAlchemyUnitOfWork(session_factory)
    with pytest.raises(MyExceptionError), uow:
        insert_work_day(uow.session, "2025-01-31")
        raise MyExceptionError
    new_session = session_factory()
    rows = list(new_session.execute(text('SELECT * FROM "work_days"')))
    assert rows == []
