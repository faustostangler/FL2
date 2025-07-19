"""SQLite-backed repository implementation for company data."""

from __future__ import annotations

from typing import List, Tuple

from domain.dto.company_data_dto import CompanyDataDTO
from domain.ports import LoggerPort, SqlAlchemyCompanyDataRepositoryPort
from infrastructure.config import Config
from infrastructure.helpers.list_flattener import ListFlattener
from infrastructure.models.company_data_model import CompanyDataModel
from infrastructure.repositories.sqlalchemy_repository_base import (
    SqlAlchemyRepositoryBase,
)


class SqlAlchemyCompanyDataRepository(
    SqlAlchemyRepositoryBase[CompanyDataDTO, int],
    SqlAlchemyCompanyDataRepositoryPort,
):
    """Concrete repository implementation for CompanyDataDTO using SQLite and
    SQLAlchemy.

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

    def save_all(self, items: List[CompanyDataDTO]) -> None:
        """Persist company DTOs using the surrogate id for updates."""
        session = self.Session()
        try:
            model, _ = self.get_model_class()
            flat_items = ListFlattener.flatten(items)
            valid_items = [i for i in flat_items if i is not None]
            for dto in valid_items:
                obj = model.from_dto(dto)
                existing = session.query(model).filter_by(cvm_code=obj.cvm_code).first()
                if existing:
                    obj.id = existing.id
                session.merge(obj)
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

        # self.logger.log(f"Load Class {self.__class__.__name__}", level="info")

    def get_model_class(self) -> Tuple[type, tuple]:
        """Return the SQLAlchemy ORM model class managed by this repository.

        Returns:
            type: The model class associated with this repository.
        """
        return CompanyDataModel, (CompanyDataModel.id,)
