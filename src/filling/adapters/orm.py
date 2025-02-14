from sqlalchemy import Column, Date, Enum, Float, ForeignKey, Integer, Table
from sqlalchemy.orm import registry, relationship

from src.filling.domain import model
from src.filling.domain.enums import EmploymentCode


mapper_registry = registry()

work_times = Table(
    "work_times",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("work_day_id", ForeignKey("work_days.id", ondelete="CASCADE"), nullable=False),
    Column("code", Enum(EmploymentCode), nullable=False),
    Column("hours", Float),
)

work_days = Table(
    "work_days",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("date", Date, nullable=False),
)


def start_mappers() -> None:
    work_time_mapper = mapper_registry.map_imperatively(model.WorkTime, work_times)

    mapper_registry.map_imperatively(
        model.WorkDay,
        work_days,
        properties={
            "_shift": relationship(
                work_time_mapper,
                collection_class=set,
            )
        },
    )
