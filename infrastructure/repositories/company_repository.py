"""SQLite-backed repository implementation for company data."""

from __future__ import annotations

from typing import List, Set

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
    SqlAlchemyRepositoryBase[CompanyDTO],
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

    def get_all(self) -> List[CompanyDTO]:
        """Retrieve all persisted companies from the database.

        Returns:
            List[CompanyDTO]: A list of all stored companies as DTOs.
        """
        session = self.Session()
        try:
            results = session.query(CompanyModel).all()
            return [model.to_dto() for model in results]
        finally:
            session.close()

    def has_item(self, identifier: str) -> bool:
        """Check if a company exists by CVM code.

        Args:
            identifier (str): CVM code of the company.

        Returns:
            bool: True if the company exists, False otherwise.
        """
        session = self.Session()
        try:
            return (
                session.query(CompanyModel)
                .filter_by(cvm_code=identifier)
                .first()
                is not None
            )
        finally:
            session.close()

    def get_by_id(self, id: str) -> CompanyDTO:
        """Retrieve a company by its CVM code.

        Args:
            id (str): CVM code of the company.

        Returns:
            CompanyDTO: The matching company DTO.

        Raises:
            ValueError: If no company with the given CVM code is found.
        """
        session = self.Session()
        try:
            obj = session.query(CompanyModel).filter_by(cvm_code=id).first()
            if not obj:
                raise ValueError(f"Company not found: {id}")
            return obj.to_dto()
        finally:
            session.close()

    def get_all_primary_keys(self) -> Set[str]:
        """Retrieve all persisted CVM codes (primary keys).

        Returns:
            Set[str]: A set of distinct CVM codes currently stored.
        """
        session = self.Session()
        try:
            results = session.query(CompanyModel.cvm_code).distinct().all()
            return {row[0] for row in results if row[0]}
        finally:
            session.close()
