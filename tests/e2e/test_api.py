from datetime import date
from typing import TYPE_CHECKING

import pytest
from litestar.status_codes import HTTP_200_OK
from sqlalchemy.ext.asyncio import AsyncSession

from src.filling.domain import model


if TYPE_CHECKING:
    from httpx import AsyncClient

pytestmark = pytest.mark.anyio


async def test_health_check(test_client: "AsyncClient") -> None:
    response = await test_client.get("/health-check")
    assert response.status_code == HTTP_200_OK
    assert response.text == "healthy"


@pytest.fixture
async def add_work_days(session: AsyncSession) -> None:
    session.add(model.WorkDay(date=date(2025, 1, 1)))
    session.add(model.WorkDay(date=date(2025, 1, 2)))
    session.add(model.WorkDay(date=date(2025, 2, 1)))
    await session.commit()


@pytest.mark.usefixtures("add_work_days")
async def test_returns_work_days(test_client: "AsyncClient") -> None:
    response = await test_client.get("/api/v1/workdays")
    assert response.status_code == HTTP_200_OK
    assert response.json() == [{"date": "2025-01-01"}, {"date": "2025-01-02"}, {"date": "2025-02-01"}]


@pytest.mark.skip
@pytest.mark.usefixtures("add_work_days")
async def test_returns_work_days_for_the_month(test_client: "AsyncClient") -> None:
    response = await test_client.get("/api/v1/month/2025/1")
    assert response.status_code == HTTP_200_OK
    assert response.json() == [{"date": "2025-01-01"}, {"date": "2025-01-02"}]
