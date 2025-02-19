import abc

from advanced_alchemy.repository import SQLAlchemySyncRepository
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.filling import config
from src.filling.adapters import repository
from src.filling.domain import model as m


DEFAULT_SESSION_FACTORY = sessionmaker(
    bind=create_engine(
        config.get_postgres_uri(),
    )
)


class AbstractUnitOfWork(abc.ABC):
    work_days: SQLAlchemySyncRepository[m.WorkDay]  # type: ignore[type-var]

    def __enter__(self) -> "AbstractUnitOfWork":
        return self

    def __exit__(self, *args: object) -> None:
        self.rollback()

    @abc.abstractmethod
    def commit(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self) -> None:
        raise NotImplementedError


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self.session_factory = session_factory

    def __enter__(self) -> "AbstractUnitOfWork":
        self.session = self.session_factory()
        self.work_days = repository.SqlAlchemyRepository(session=self.session)
        return super().__enter__()

    def __exit__(self, *args: object) -> None:
        super().__exit__(*args)
        self.session.close()

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()
