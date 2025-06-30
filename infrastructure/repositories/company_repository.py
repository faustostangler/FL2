from __future__ import annotations

from typing import List, Set

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from domain.dto.company_dto import CompanyDTO
from domain.ports import CompanyRepositoryPort
from infrastructure.config import Config
from infrastructure.logging import Logger
from infrastructure.models.base import Base
from infrastructure.models.company_model import CompanyModel


class SQLiteCompanyRepository(CompanyRepositoryPort):
    """Concrete implementation of the company repository using SQLite."""

    def __init__(self, config: Config, logger: Logger):
        """Initialize the SQLite database connection and ensure tables
        exist."""
        self.config = config
        self.logger = logger
        self.logger.log("Start SQLiteCompanyRepository", level="info")

        self.engine = create_engine(
            config.database.connection_string,
            connect_args={"check_same_thread": False},
        )
        with self.engine.connect() as conn:
            conn.execute(text("PRAGMA journal_mode=WAL"))
        self.Session = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)

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
