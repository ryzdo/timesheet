import abc
from collections.abc import Sequence
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.filling.domain import model


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, batch: model.WorkDay) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, date: date) -> model.WorkDay | None:
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, work_day: model.WorkDay) -> None:
        self.session.add(work_day)

    def get(self, date: date) -> model.WorkDay | None:
        return self.session.scalar(select(model.WorkDay).filter_by(date=date))

    def list(self) -> Sequence[model.WorkDay]:
        return self.session.scalars(select(model.WorkDay)).all()
