from advanced_alchemy.repository import SQLAlchemySyncRepository

from src.filling.domain import model as m


class SqlAlchemyRepository(SQLAlchemySyncRepository[m.WorkDay]):  # type: ignore[type-var]
    model_type = m.WorkDay
