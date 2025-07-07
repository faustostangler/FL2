from abc import ABC, abstractmethod
from typing import List, TypeVar

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from domain.ports import LoggerPort
from domain.ports.base_repository_port import BaseRepositoryPort
from infrastructure.config import Config
from infrastructure.models.base_model import BaseModel

T = TypeVar("T")  # T pode ser CompanyDTO, StatementDTO, etc.


class BaseRepository(BaseRepositoryPort[T], ABC):
    """
    Contract - Interface genérica para repositórios de leitura/escrita.
    Pode ser especializada para qualquer tipo de DTO.
    """

    def __init__(self, config: Config, logger: LoggerPort):
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
    def save_all(self, items: List[T]) -> None:
        """Saves in repository."""
        pass

    @abstractmethod
    def get_all(self) -> List[T]:
        """Get all items from repository."""
        pass

    @abstractmethod
    def has_item(self, identifier: str) -> bool:
        """Check if it is in repository."""
        pass

    @abstractmethod
    def get_by_id(self, id: str) -> T:
        """Recupera uma empresa a partir do ticker."""
        pass
