from typing import Any

from litestar import Litestar, MediaType, get
from litestar.plugins.sqlalchemy import SQLAlchemyAsyncConfig, SQLAlchemyPlugin
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import get_postgres_uri
from src.filling.adapters.orm import mapper_registry, start_mappers
from src.filling.domain import model


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


app = Litestar(
    route_handlers=[health_check, get_list_work_days], plugins=[SQLAlchemyPlugin(db_config)], on_startup=[start_mappers]
)
