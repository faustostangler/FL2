"""SQLite-backed repository implementation for company data."""

from __future__ import annotations

from typing import List, Set

from domain.dto.company_dto import CompanyDTO
from domain.ports import CompanyRepositoryPort, LoggerPort
from infrastructure.config import Config
from infrastructure.models.company_model import CompanyModel
from infrastructure.repositories import BaseRepository


class SqlAlchemyCompanyRepository(BaseRepository[CompanyDTO], CompanyRepositoryPort):
    """Concrete implementation of the repository using SQLite.

    Note:
        This repository uses `check_same_thread=False` for SQLite connections,
        which allows connections to be shared across threads. Ensure that
        session and connection usage is properly managed to avoid thread-safety
        issues.
    """

    def __init__(self, config: Config, logger: LoggerPort):
        super().__init__(config, logger)

        # self.logger.log(f"Load Class {self.__class__.__name__}", level="info")

    def save_all(self, items: List[CompanyDTO]) -> None:
        """Persist a list of ``CompanyDTO`` objects."""
        session = self.Session()
        try:
            models = [CompanyModel.from_dto(dto) for dto in items]
            for model in models:
                session.merge(model)
            session.commit()
            self.logger.log(
                f"Saved {len(items)} companies",
                level="info",
            )
        except Exception as e:
            session.rollback()
            self.logger.log(
                f"Failed to save companies: {e}",
                level="error",
            )
            raise
        finally:
            session.close()

    def get_all(self) -> List[CompanyDTO]:
        """Return every persisted company."""
        session = self.Session()
        try:
            results = session.query(CompanyModel).all()
            return [model.to_dto() for model in results]
        finally:
            session.close()

    def has_item(self, identifier: str) -> bool:
        """Check if a company exists for the given CVM code."""
        session = self.Session()
        try:
            return (
                session.query(CompanyModel).filter_by(cvm_code=identifier).first()
                is not None
            )
        finally:
            session.close()

    def get_by_id(self, id: str) -> CompanyDTO:
        """Retrieve a company by CVM code or raise ``ValueError`` if
        missing."""
        session = self.Session()
        try:
            obj = session.query(CompanyModel).filter_by(cvm_code=id).first()
            if not obj:
                raise ValueError(f"Company not found: {id}")
            return obj.to_dto()

        finally:
            session.close()

    def get_all_primary_keys(self) -> Set[str]:
        """Return a set of all CVM codes already persisted."""
        session = self.Session()
        try:
            results = session.query(CompanyModel.cvm_code).distinct().all()
            return {row[0] for row in results if row[0]}
        finally:
            session.close()
