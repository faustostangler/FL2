"""SQLite-backed repository implementation for company data."""

from __future__ import annotations

from typing import Tuple

from domain.dto.company_data_dto import CompanyDataDTO
from domain.ports import LoggerPort, SqlAlchemyCompanyDataRepositoryPort
from infrastructure.config import Config
from infrastructure.models.company_data_model import CompanyDataModel
from infrastructure.repositories.sqlalchemy_repository_base import (
    SqlAlchemyRepositoryBase,
)


class SqlAlchemyCompanyDataRepository(
    SqlAlchemyRepositoryBase[CompanyDataDTO, str],
    SqlAlchemyCompanyDataRepositoryPort,
):
    """Concrete repository implementation for CompanyDataDTO using SQLite and SQLAlchemy.

    This adapter implements the CompanyDataRepositoryPort interface, providing persistence
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
        super().__init__(config, logger) 

        self.config = config
        self.logger = logger

        # self.logger.log(f"Load Class {self.__class__.__name__}", level="info")

    def get_model_class(self) -> Tuple[type, tuple]:
        """Return the SQLAlchemy ORM model class managed by this repository.

        Returns:
            type: The model class associated with this repository.
        """
        return CompanyDataModel, (CompanyDataModel.cvm_code,)  # para PK simples
