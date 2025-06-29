from __future__ import annotations
import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("infrastructure > company_repository")

from typing import List

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from domain.dto.company_dto import CompanyDTO
from domain.ports import CompanyRepositoryPort
from infrastructure.config import Config
from infrastructure.logging import Logger
from infrastructure.models.company_model import Base, CompanyModel
from infrastructure.repositories.base_repository import BaseRepository


class SQLiteCompanyRepository(BaseRepository[CompanyDTO], CompanyRepositoryPort):
    """
    Concrete implementation of BaseRepository for CompanyDTO,
    using SQLite and SQLAlchemy for persistence.
    """
    import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("company_repository.SQLiteCompanyRepository(BaseRepository[CompanyDTO], CompanyRepositoryPort)")

    def __init__(self, config: Config, logger: Logger):
        """
        Initializes the SQLite database connection and ensures table creation.
        """
        import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("SQLiteCompanyRepository(BaseRepository[CompanyDTO], CompanyRepositoryPort).__init__")
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
        """
        Saves or updates a list of CompanyDTOs into the database.

        :param items: List of CompanyDTO instances to persist
        """
        import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("SQLiteCompanyRepository(BaseRepository[CompanyDTO], CompanyRepositoryPort).save_all()")
        session = self.Session()
        try:
            models = [CompanyModel.from_dto(dto) for dto in items]
            session.bulk_save_objects(models)
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
        """
        Retrieves all companies from the database.

        :return: A list of CompanyDTOs
        """
        import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("SQLiteCompanyRepository(BaseRepository[CompanyDTO], CompanyRepositoryPort).get_all()")
        session = self.Session()
        try:
            results = session.query(CompanyModel).all()
            return [obj.to_dto() for obj in results]
        finally:
            session.close()

    def has_item(self, identifier: str) -> bool:
        """
        Checks if a company with the given CVM code exists in the database.

        :param identifier: CVM code to verify
        :return: True if the company exists, False otherwise
        """
        import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("SQLiteCompanyRepository(BaseRepository[CompanyDTO], CompanyRepositoryPort).has_item()")
        session = self.Session()
        try:
            return (
                session.query(CompanyModel).filter_by(cvm_code=identifier).first()
                is not None
            )
        finally:
            session.close()

    def get_by_id(self, id: str) -> CompanyDTO:
        """
        Retrieves a single company from the database by CVM code.

        :param id: The CVM code identifier
        :return: A CompanyDTO representing the retrieved company
        :raises ValueError: If no company is found
        """
        import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("SQLiteCompanyRepository(BaseRepository[CompanyDTO], CompanyRepositoryPort).get_by_id()")
        session = self.Session()
        try:
            obj = session.query(CompanyModel).filter_by(cvm_code=id).first()
            if not obj:
                raise ValueError(f"Company not found: {id}")
            return obj.to_dto()

        finally:
            session.close()

    def get_all_primary_keys(self) -> set[str]:
        """
        Retorna um conjunto com todos os códigos CVM já salvos no banco.

        :return: Conjunto de códigos CVM únicos.
        """
        import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("SQLiteCompanyRepository(BaseRepository[CompanyDTO], CompanyRepositoryPort).get_all_primary_keys()")
        session = self.Session()
        try:
            results = session.query(CompanyModel.cvm_code).distinct().all()
            return {row[0] for row in results if row[0]}
        finally:
            session.close()
