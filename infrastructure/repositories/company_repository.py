from sqlalchemy import create_engine, Column, String
from sqlalchemy.orm import declarative_base, sessionmaker
from typing import List

from config.config import Config
from infrastructure.repositories.base_repository import BaseRepository
from domain.models.company_dto import CompanyDTO

# Load global configuration
config = Config()

# SQLAlchemy base for ORM models
Base = declarative_base()

class CompanyModel(Base):
    """
    ORM mapping class representing the 'company' table in the database.
    This model reflects the structure of the tbl_company table as defined in the config and CompanyDTO.
    """
    __tablename__ = config.databases["default"]["tables"]["company"]

    ticker = Column(String, primary_key=True)
    company_name = Column(String)
    cnpj = Column(String)
    cvm_code = Column(String)
    ticker_codes = Column(String)
    isin_codes = Column(String)
    trading_name = Column(String)
    sector = Column(String)
    subsector = Column(String)
    segment = Column(String)
    listing = Column(String)
    activity = Column(String)
    registrar = Column(String)
    website = Column(String)


class SQLiteCompanyRepository(BaseRepository[CompanyDTO]):
    """
    Concrete implementation of BaseRepository for CompanyDTO,
    using SQLite and SQLAlchemy for persistence.
    """

    def __init__(self):
        """
        Initializes the SQLite database connection and ensures table creation.
        """
        self.engine = create_engine(f"sqlite:///{config.paths['db_file']}")
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
                obj = CompanyModel(
                    ticker=dto.ticker,
                    company_name=dto.company_name,
                    cnpj=dto.cnpj,
                    cvm_code=dto.cvm_code,
                    ticker_codes=dto.ticker_codes,
                    isin_codes=dto.isin_codes,
                    trading_name=dto.trading_name,
                    sector=dto.sector,
                    subsector=dto.subsector,
                    segment=dto.segment,
                    listing=dto.listing,
                    activity=dto.activity,
                    registrar=dto.registrar,
                    website=dto.website
                )
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
            return [self._to_dto(obj) for obj in results]
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
            return self._to_dto(obj)
        finally:
            session.close()

    def _to_dto(self, obj: CompanyModel) -> CompanyDTO:
        """
        Internal method to convert a SQLAlchemy model to a CompanyDTO.

        :param obj: ORM instance (CompanyModel)
        :return: Domain DTO (CompanyDTO)
        """
        return CompanyDTO(
            ticker=obj.ticker,                  # type: ignore
            company_name=obj.company_name,      # type: ignore
            cnpj=obj.cnpj,                      # type: ignore
            cvm_code=obj.cvm_code,              # type: ignore
            ticker_codes=obj.ticker_codes,      # type: ignore
            isin_codes=obj.isin_codes,          # type: ignore
            trading_name=obj.trading_name,      # type: ignore
            sector=obj.sector,                  # type: ignore
            subsector=obj.subsector,            # type: ignore
            segment=obj.segment,                # type: ignore
            listing=obj.listing,                # type: ignore
            activity=obj.activity,              # type: ignore
            registrar=obj.registrar,            # type: ignore
            website=obj.website,                # type: ignore
        )
