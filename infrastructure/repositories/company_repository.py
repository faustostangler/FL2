from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import List

import utils.logging as logging_utils
from config import Config
from infrastructure.repositories.base_repository import BaseRepository
from domain.dto.company_dto import CompanyDTO
from infrastructure.orm.company_model import Base, CompanyModel

# Load global configuration
config = Config()

class SQLiteCompanyRepository(BaseRepository[CompanyDTO]):
    """
    Concrete implementation of BaseRepository for CompanyDTO,
    using SQLite and SQLAlchemy for persistence.
    """

    def __init__(self):
        """
        Initializes the SQLite database connection and ensures table creation.
        """
        logging_utils.log_message("Start SQLiteCompanyRepository", level="info")
        self.engine = create_engine(config.database.connection_string)
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
        Checks if a company with the given ticker exists in the database.

        :param identifier: Ticker symbol to verify
        :return: True if the company exists, False otherwise
        """
        session = self.Session()
        try:
            return session.query(CompanyModel).filter_by(ticker=identifier).first() is not None
        finally:
            session.close()

    def get_by_id(self, id: str) -> CompanyDTO:
        """
        Retrieves a single company from the database by ticker.

        :param id: The ticker identifier
        :return: A CompanyDTO representing the retrieved company
        :raises ValueError: If no company is found
        """
        session = self.Session()
        try:
            obj = session.query(CompanyModel).filter_by(ticker=id).first()
            if not obj:
                raise ValueError(f"Company not found: {id}")
            return obj.to_dto()

        finally:
            session.close()

    def get_all_cvm_codes(self) -> set[str]:
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

