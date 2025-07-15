from abc import ABC, abstractmethod
from typing import Any, List, TypeVar

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from domain.ports import LoggerPort
from domain.ports.base_repository_port import SqlAlchemyRepositoryBasePort
from infrastructure.config import Config
from infrastructure.helpers.list_flattener import ListFlattener
from infrastructure.models.base_model import BaseModel

T = TypeVar("T")  # T pode ser CompanyDTO, StatementDTO, etc.


class SqlAlchemyRepositoryBase(SqlAlchemyRepositoryBasePort[T, Any], ABC):
    """
    Contract - Interface genérica para repositórios de leitura/escrita.
    Pode ser especializada para qualquer tipo de DTO.
    """

    def __init__(self, config: Config, logger: LoggerPort) -> None:
        """Initialize the repository infrastructure: engine, session, and schema.

        This constructor sets up the SQLite engine with threading support,
        configures the session factory for ORM transactions, and ensures
        that all declared models are created in the database.

        Args:
            config (Config): Application configuration containing the database connection string.
            logger (LoggerPort): Logger used for emitting repository lifecycle messages.
        """
        # Store configuration and logger for use throughout the repository
        self.config = config
        self.logger = logger

        # Create SQLAlchemy engine for SQLite with thread-safe settings
        self.engine = create_engine(
            config.database.connection_string,
            connect_args={"check_same_thread": False},  # allow usage from multiple threads
            future=True,
        )

        # Enable Write-Ahead Logging mode to support concurrent reads/writes
        with self.engine.connect() as conn:
            conn.execute(text("PRAGMA journal_mode=WAL"))

        # Create a session factory for managing DB transactions
        self.Session = sessionmaker(
            bind=self.engine,
            autoflush=True,
            expire_on_commit=True,
        )

        # Automatically create all tables defined in the SQLAlchemy models
        BaseModel.metadata.create_all(self.engine)

        # self.logger.log(f"Create Instance Base Class {self.__class__.__name__}", level="info")

    @abstractmethod
    def get_model_class(self) -> type:
        """Return the SQLAlchemy model class associated with the DTO.

        This method must be implemented by subclasses to specify which
        SQLAlchemy ORM model corresponds to the generic DTO type `T`.

        Returns:
            type: The SQLAlchemy ORM model class.

        Raises:
            NotImplementedError: If the method is not overridden by a subclass.
        """
        # Must be implemented by subclass to define the ORM mapping
        raise NotImplementedError


    def save_all(self, items: List[T]) -> None:
        """Persist a list of DTOs in bulk.

        Args:
            items (List[T]): A list (possibly nested) of DTOs to be persisted.
        """
        # Create a new SQLAlchemy session
        session = self.Session()

        # Retrieve the SQLAlchemy model class associated with the DTO type
        model = self.get_model_class()

        try:
            # Flatten nested lists into a single-level list of DTOs
            flat_items = ListFlattener.flatten(items)

            # Remove any None values from the list
            valid_items = [
                item for item in flat_items
                if item is not None
            ]

            # Merge each DTO into the current session (insert or update)
            for dto in valid_items:
                session.merge(model.from_dto(dto))

            # Commit the transaction to persist all changes
            session.commit()

            # Log the number of successfully saved items
            if len(valid_items) > 0:
                self.logger.log(
                    f"Saved {len(valid_items)} items",
                    level="info",
                )
        except Exception as e:
            # Roll back the transaction in case of error
            session.rollback()

            # Log the failure reason
            self.logger.log(
                f"Failed to save items: {e}",
                level="error",
            )

            # Re-raise the exception to propagate the error
            raise
        finally:
            # Ensure the session is always closed after execution
            session.close()
