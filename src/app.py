from collections.abc import Mapping
from datetime import date
from typing import Any

from litestar import Controller, Litestar, MediaType, get, post
from litestar.di import Provide
from litestar.logging import LoggingConfig
from litestar.plugins.sqlalchemy import SQLAlchemyAsyncConfig, SQLAlchemyPlugin
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import get_postgres_uri
from src.filling.adapters.orm import mapper_registry, start_mappers
from src.filling.domain import model
from src.filling.service_layer.services import WorkDayService, provide_work_days_service


WorkDayType = dict[str, Any]


def serialize(wd: model.WorkDay) -> WorkDayType:
    return {"date": wd.date}


@get(path="/health-check", media_type=MediaType.TEXT)
async def health_check() -> str:
    return "healthy"


@get(path="/api/v1/workdays")
async def get_list_work_days(db_session: AsyncSession) -> list[WorkDayType]:
    query = select(model.WorkDay)
    result = await db_session.execute(query)
    r = result.scalars().all()
    return [serialize(wd) for wd in r]


db_config = SQLAlchemyAsyncConfig(
    connection_string=get_postgres_uri(),
    metadata=mapper_registry.metadata,
    create_all=True,
    before_send_handler="autocommit",
)


class WorkDayController(Controller):
    """Author CRUD endpoints."""

    path = "/api/v2/workdays"
    dependencies: Mapping[str, Provide] = {"work_days_service": Provide(provide_work_days_service)}

    @get()
    async def get_list_work_days2(self, work_days_service: WorkDayService) -> list[WorkDayType]:
        return [serialize(wd) for wd in await work_days_service.list()]

    @post()
    async def create_work_day(
        self,
        work_days_service: WorkDayService,
        date: date,
    ) -> date:
        """Create a new author."""
        obj = await work_days_service.create({"date": date})
        return obj.date


logging_config = LoggingConfig(
    root={"level": "INFO", "handlers": ["queue_listener"]},
    formatters={"standard": {"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"}},
    log_exceptions="always",
)

app = Litestar(
    route_handlers=[health_check, get_list_work_days, WorkDayController],
    plugins=[SQLAlchemyPlugin(db_config)],
    on_startup=[start_mappers],
    logging_config=logging_config,
)
