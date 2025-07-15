"""SQLite-backed repository implementation for company data."""

from __future__ import annotations

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from domain.dto.company_dto import CompanyDTO
from domain.ports import LoggerPort, SqlAlchemyCompanyRepositoryPort
from infrastructure.config import Config
from infrastructure.models.base_model import BaseModel
from infrastructure.models.company_model import CompanyModel
from infrastructure.repositories.sqlalchemy_repository_base import (
    SqlAlchemyRepositoryBase,
)


class SqlAlchemyCompanyRepository(
    SqlAlchemyRepositoryBase[CompanyDTO, str],
    SqlAlchemyCompanyRepositoryPort,
):
    """Concrete repository implementation for CompanyDTO using SQLite and SQLAlchemy.

    This adapter implements the CompanyRepositoryPort interface, providing persistence
    operations for company data via a local SQLite database.

    Note:
        Uses `check_same_thread=False` to support multithreading. Make sure session
        usage is isolated per thread to avoid concurrency issues.

        Write-Ahead Logging (WAL) mode is enabled to improve concurrent read/write behavior.
    """

    def __init__(self, config: Config, logger: LoggerPort) -> None:
        """Initialize the SQLite-backed company repository.

        Args:
            config (Config): Application configuration with database connection details.
            logger (LoggerPort): Logging adapter used for tracking internal behavior.
        """
        self.config = config
        self.logger = logger

        # Create SQLAlchemy engine with threading support for SQLite
        self.engine = create_engine(
            config.database.connection_string,
            connect_args={"check_same_thread": False},
            future=True,
        )

        # Enable Write-Ahead Logging for concurrent access
        with self.engine.connect() as conn:
            conn.execute(text("PRAGMA journal_mode=WAL"))

        # Configure session factory
        self.Session = sessionmaker(
            bind=self.engine, autoflush=True, expire_on_commit=True
        )

        # Create all mapped tables if they do not exist yet
        BaseModel.metadata.create_all(self.engine)

        # self.logger.log(f"Load Class {self.__class__.__name__}", level="info")

    def get_model_class(self) -> type:
        """Return the SQLAlchemy ORM model class managed by this repository.

        Returns:
            type: The model class associated with this repository.
        """
        return CompanyModel

