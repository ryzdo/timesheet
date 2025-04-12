from collections.abc import AsyncGenerator
from datetime import date

from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService
from sqlalchemy.ext.asyncio import AsyncSession

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


class WorkDayService(SQLAlchemyAsyncRepositoryService[model.WorkDay]):  # type: ignore[type-var]
    class WorkDayRepository(SQLAlchemyAsyncRepository[model.WorkDay]):  # type: ignore[type-var]
        model_type = model.WorkDay

    repository_type = WorkDayRepository


async def provide_work_days_service(db_session: AsyncSession) -> AsyncGenerator[WorkDayService]:
    async with WorkDayService.new(session=db_session) as service:
        yield service
