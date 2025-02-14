from datetime import datetime

from sqlalchemy import text
from sqlalchemy.orm import Session

from src.filling.adapters import repository
from src.filling.domain import model
from src.filling.domain.enums import EmploymentCode


def test_repository_can_save_a_work_day(session: Session) -> None:
    wday = model.WorkDay(datetime.fromisoformat("2025-01-31"))

    repo = repository.SqlAlchemyRepository(session)
    repo.add(wday)
    session.commit()

    rows = session.execute(text("SELECT date FROM work_days"))
    assert list(rows) == [("2025-01-31",)]


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


def insert_work_time(session: Session, work_day_id: int, code: EmploymentCode, hours: float) -> None:
    session.execute(
        text("INSERT INTO work_times (work_day_id, code, hours) VALUES (:work_day_id, :code, :hours)"),
        {"work_day_id": work_day_id, "code": code.name, "hours": hours},
    )


def test_repository_can_retrieve_a_work_day_with_shift(session: Session) -> None:
    wday_id = insert_work_day(session, "2025-01-30")
    insert_work_day(session, "2025-01-31")
    insert_work_time(session, wday_id, EmploymentCode.DAY_HOUR, 3.0)
    insert_work_time(session, wday_id, EmploymentCode.NIGHT_HOUR, 8.0)

    repo = repository.SqlAlchemyRepository(session)
    retrieved = repo.get(datetime.fromisoformat("2025-01-30").date())

    expected = model.WorkDay(datetime.fromisoformat("2025-01-30").date())
    assert retrieved == expected
    assert retrieved._shift == {
        model.WorkTime(EmploymentCode.DAY_HOUR, 3),
        model.WorkTime(EmploymentCode.NIGHT_HOUR, 8),
    }
