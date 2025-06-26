from typing import List
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from infrastructure.repositories.base_repository import BaseRepository
from infrastructure.models.company_model import Base, CompanyModel
from domain.dto.company_dto import CompanyDTO
from infrastructure.config import Config
from infrastructure.logging import Logger


class SQLiteCompanyRepository(BaseRepository[CompanyDTO]):
    """
    Concrete implementation of BaseRepository for CompanyDTO,
    using SQLite and SQLAlchemy for persistence.
    """

    def __init__(self, config: Config, logger: Logger):
        """
        Initializes the SQLite database connection and ensures table creation.
        """
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
        session = self.Session()
        try:
            for dto in items:
                obj = CompanyModel.from_dto(dto)
                session.merge(obj)  # Upsert operation: insert or update if exists
            session.commit()
        except Exception as e:
            self.logger.log(f"erro {e}", level="debug")
        finally:
            session.close()

    def get_all(self) -> List[CompanyDTO]:
        """
        Retrieves all companies from the database.

        :return: A list of CompanyDTOs
        """
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
        session = self.Session()
        try:
            results = session.query(CompanyModel.cvm_code).distinct().all()
            return {row[0] for row in results if row[0]}
        finally:
            session.close()
