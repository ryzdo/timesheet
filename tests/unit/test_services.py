from collections.abc import AsyncGenerator, Generator, Sequence
from datetime import date, datetime
from typing import cast
from unittest.mock import AsyncMock

import pytest
from advanced_alchemy.exceptions import RepositoryError
from pytest_mock import MockerFixture
from sqlalchemy import Engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import clear_mappers

from src.filling.adapters import repository
from src.filling.adapters.orm import start_mappers
from src.filling.domain import model
from src.filling.domain.enums import EmploymentCode
from src.filling.domain.model import WorkDay
from src.filling.service_layer import services, unit_of_work
from src.filling.service_layer.services import WorkDayService


pytestmark = pytest.mark.anyio


@pytest.fixture(autouse=True, scope="module")
def setup_mappers() -> Generator[None]:
    """Выполняет маппинг перед тестами."""
    start_mappers()
    yield
    clear_mappers()


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


class TestWorkDayServiceMock:
    @pytest.fixture
    async def mock_session(self, mocker: MockerFixture) -> AsyncMock:
        mock_engine = mocker.MagicMock(spec=Engine)
        mock_engine.dialect = mocker.MagicMock()

        session = mocker.AsyncMock(spec=AsyncSession)
        session.bind = mock_engine
        session.execute.return_value = mocker.AsyncMock(scalar_one_or_none=mocker.AsyncMock(return_value=None))
        return cast("AsyncMock", session)

    @pytest.fixture
    async def workday_service(self, mock_session: AsyncSession) -> AsyncGenerator[WorkDayService]:
        async with WorkDayService.new(session=mock_session) as service:
            yield service

    async def test_create_workday(
        self,
        workday_service: WorkDayService,
    ) -> None:
        test_date = date(2023, 1, 1)
        test_work_day = WorkDay(date=test_date)

        created = await workday_service.create(test_work_day, auto_commit=True)

        assert created == test_work_day
        assert created.date == test_date
        workday_service.repository.session.add.assert_called_once_with(test_work_day)
        workday_service.repository.session.commit.assert_called_once()
        workday_service.repository.session.flush.assert_not_called()

    async def test_create_workday_no_autocommit(
        self,
        workday_service: WorkDayService,
    ) -> None:
        test_work_day = WorkDay(date=date(2023, 1, 1))

        await workday_service.create(test_work_day)

        workday_service.repository.session.add.assert_called_once()
        workday_service.repository.session.commit.assert_not_called()
        workday_service.repository.session.flush.assert_called_once()

    @pytest.mark.skip(reason="Не работает в рамках тестов")
    async def test_create_duplicate_workday_fails(
        self,
        workday_service: WorkDayService,
    ) -> None:
        test_date = date(2023, 1, 1)
        existing_workday = WorkDay(date=test_date)
        new_workday = WorkDay(date=test_date)

        await workday_service.create(existing_workday, auto_commit=True)

        with pytest.raises(RepositoryError):
            await workday_service.create(new_workday, auto_commit=True)
        workday_service.repository.session.add.assert_not_awaited()
        workday_service.repository.session.commit.assert_not_awaited()
