from datetime import date

from src.filling.domain import model
from src.filling.domain.enums import EmploymentCode
from src.filling.service_layer import unit_of_work


class InvalidDateError(Exception):
    pass


def add_work_day(
    date: date,
    uow: unit_of_work.AbstractUnitOfWork,
) -> None:
    with uow:
        uow.work_days.add(model.WorkDay(date))
        uow.commit()


def add_work_time(
    date: date,
    code: EmploymentCode,
    hours: float,
    uow: unit_of_work.AbstractUnitOfWork,
) -> None:
    with uow:
        wday = uow.work_days.get(date)
        if wday is None:
            raise InvalidDateError("Invalid date")
        wday.add_work_time(model.WorkTime(code, hours))
        uow.commit()
