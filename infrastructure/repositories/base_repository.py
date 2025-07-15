from abc import ABC, abstractmethod
from typing import Any, List, TypeVar

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from domain.ports import LoggerPort
from domain.ports.base_repository_port import BaseRepositoryPort
from infrastructure.config import Config
from infrastructure.helpers.list_flattener import ListFlattener
from infrastructure.models.base_model import BaseModel

T = TypeVar("T")  # T pode ser CompanyDTO, StatementDTO, etc.


class BaseRepository(BaseRepositoryPort[T, Any], ABC):
    """
    Contract - Interface genérica para repositórios de leitura/escrita.
    Pode ser especializada para qualquer tipo de DTO.
    """

    def __init__(self, config: Config, logger: LoggerPort) -> None:
        """Initialize the SQLite database connection and ensure tables
        exist."""
        self.config = config
        self.logger = logger

        self.engine = create_engine(
            config.database.connection_string,
            connect_args={"check_same_thread": False},
            future=True,
        )
        with self.engine.connect() as conn:
            conn.execute(text("PRAGMA journal_mode=WAL"))

        self.Session = sessionmaker(
            bind=self.engine, autoflush=True, expire_on_commit=True
        )
        BaseModel.metadata.create_all(self.engine)

        # self.logger.log(f"Create Instance Base Class {self.__class__.__name__}", level="info")
    @abstractmethod
    def get_model_class(self) -> type:
        """Return the SQLAlchemy model class associated with the DTO."""
        raise NotImplementedError


    def save_all(self, items: List[T]) -> None:
        """Persist a list of ``CompanyDTO`` objects."""
        session = self.Session()
        model = self.get_model_class()

        try:
            flat_items = ListFlattener.flatten(items)  # recebe nested lists, devolve flat list

            valid_items = [
                item for item in flat_items
                if item is not None
            ]

            for dto in valid_items:
                session.merge(model.from_dto(dto))
            session.commit()

            if len(valid_items) > 0:
                self.logger.log(
                    f"Saved {len(valid_items)} items",
                    level="info",
                )
        except Exception as e:
            session.rollback()
            self.logger.log(
                f"Failed to save items: {e}",
                level="error",
            )
            raise
        finally:
            session.close()
