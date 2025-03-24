from litestar import Litestar, MediaType, get
from litestar.plugins.sqlalchemy import SQLAlchemyAsyncConfig, SQLAlchemyPlugin

from src.config import get_postgres_uri
from src.filling.adapters.orm import mapper_registry


@get(path="/health-check", media_type=MediaType.TEXT)
async def health_check() -> str:
    return "healthy"


db_config = SQLAlchemyAsyncConfig(
    connection_string=get_postgres_uri(),
    metadata=mapper_registry.metadata,
    create_all=True,
    before_send_handler="autocommit",
)


app = Litestar(
    route_handlers=[health_check],
    plugins=[SQLAlchemyPlugin(db_config)],
)
