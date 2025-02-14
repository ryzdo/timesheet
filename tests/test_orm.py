from datetime import datetime

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from src.filling.domain import model
from src.filling.domain.enums import EmploymentCode


def test_saving_work_day(session: Session) -> None:
    wday = model.WorkDay(datetime.fromisoformat("2025-01-31"))
    session.add(wday)
    session.commit()
    rows = list(session.execute(text("SELECT date FROM work_days")))
    assert rows == [("2025-01-31",)]


def test_work_time_mapper_can_load_lines(session: Session) -> None:
    session.execute(
        text(
            "INSERT INTO work_times (work_day_id, code, hours)"
            'VALUES (1, "DAY_HOUR", 8),(2,"DAY_HOUR", 11),(2, "NIGHT_HOUR", 4)'
        )
    )
    expected = [
        model.WorkTime(EmploymentCode.DAY_HOUR, 8),
        model.WorkTime(EmploymentCode.DAY_HOUR, 11),
        model.WorkTime(EmploymentCode.NIGHT_HOUR, 4),
    ]
    assert session.execute(select(model.WorkTime)).scalars().all() == expected


def test_saving_work_time(session: Session) -> None:
    wday = model.WorkDay(datetime.fromisoformat("2025-01-31"))
    wtime = model.WorkTime(EmploymentCode.DAY_HOUR, 8)

    wday.add_work_time(wtime)
    session.add(wday)
    session.commit()

    rows = list(session.execute(text("SELECT code, hours FROM work_times")))
    assert rows == [("DAY_HOUR", 8)]
