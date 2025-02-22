from collections.abc import Sequence
from datetime import date, datetime

import pytest

from src.filling.adapters import repository
from src.filling.domain import model
from src.filling.domain.enums import EmploymentCode
from src.filling.service_layer import services, unit_of_work


VALID_HOURS = 3


class FakeRepository(repository.AbstractRepository):
    def __init__(self, work_days: list[model.WorkDay]) -> None:
        self._work_days = set(work_days)

    def add(self, work_day: model.WorkDay) -> None:
        self._work_days.add(work_day)

    def get(self, date: date) -> model.WorkDay | None:
        try:
            return next(b for b in self._work_days if b.date == date)
        except StopIteration:
            return None

    def list(self) -> Sequence[model.WorkDay]:
        return list(self._work_days)


class FakeUnitOfWork(unit_of_work.AbstractUnitOfWork):
    def __init__(self) -> None:
        self.work_days = FakeRepository([])
        self.committed = False

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        pass


def test_add_work_day() -> None:
    uow = FakeUnitOfWork()
    services.add_work_day(datetime.fromisoformat("2025-01-31").date(), uow)
    assert uow.work_days.get(datetime.fromisoformat("2025-01-31").date()) is not None
    assert uow.committed


def test_add_work_time() -> None:
    uow = FakeUnitOfWork()
    services.add_work_day(datetime.fromisoformat("2025-01-31").date(), uow)
    services.add_work_time(datetime.fromisoformat("2025-01-31").date(), EmploymentCode.DAY_HOUR, VALID_HOURS, uow)

    result = uow.work_days.get(datetime.fromisoformat("2025-01-31").date())
    assert uow.committed
    assert result is not None
    assert result.total_hours == VALID_HOURS


def test_add_work_time_errors_for_invalid_date() -> None:
    uow = FakeUnitOfWork()

    with pytest.raises(services.InvalidDateError, match="Invalid date"):
        services.add_work_time(datetime.fromisoformat("2025-01-31").date(), EmploymentCode.DAY_HOUR, VALID_HOURS, uow)
