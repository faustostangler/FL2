from sqlalchemy import create_engine, Column, String
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from typing import List, Optional

import utils.logging as logging_utils
from config import Config
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
    __tablename__ = config.database.tables["company"]

    ticker: Mapped[str] = mapped_column(primary_key=True)
    company_name: Mapped[str] = mapped_column()
    cnpj: Mapped[Optional[str]] = mapped_column()
    cvm_code: Mapped[Optional[str]] = mapped_column()
    ticker_codes: Mapped[Optional[str]] = mapped_column()
    isin_codes: Mapped[Optional[str]] = mapped_column()
    trading_name: Mapped[Optional[str]] = mapped_column()
    sector: Mapped[Optional[str]] = mapped_column()
    subsector: Mapped[Optional[str]] = mapped_column()
    segment: Mapped[Optional[str]] = mapped_column()
    listing: Mapped[Optional[str]] = mapped_column()
    activity: Mapped[Optional[str]] = mapped_column()
    registrar: Mapped[Optional[str]] = mapped_column()
    website: Mapped[Optional[str]] = mapped_column()

    company_type: Mapped[Optional[str]] = mapped_column()
    status: Mapped[Optional[str]] = mapped_column()
    b3_code: Mapped[Optional[str]] = mapped_column()
    company_category: Mapped[Optional[str]] = mapped_column()
    corporate_name: Mapped[Optional[str]] = mapped_column()
    registration_date: Mapped[Optional[str]] = mapped_column()
    start_situation_date: Mapped[Optional[str]] = mapped_column()
    situation: Mapped[Optional[str]] = mapped_column()
    situation_date: Mapped[Optional[str]] = mapped_column()
    country: Mapped[Optional[str]] = mapped_column()
    state: Mapped[Optional[str]] = mapped_column()
    city: Mapped[Optional[str]] = mapped_column()


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
                    website=dto.website, 

                    company_type=dto.company_type,
                    status=dto.status,
                    b3_code=dto.b3_code,
                    company_category=dto.company_category,
                    corporate_name=dto.corporate_name,
                    registration_date=dto.registration_date,
                    start_situation_date=dto.start_situation_date,
                    situation=dto.situation,
                    situation_date=dto.situation_date,
                    country=dto.country,
                    state=dto.state,
                    city=dto.city,
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
            ticker=obj.ticker,
            company_name=obj.company_name,
            cnpj=obj.cnpj,
            cvm_code=obj.cvm_code,
            ticker_codes=obj.ticker_codes,
            isin_codes=obj.isin_codes,
            trading_name=obj.trading_name,
            sector=obj.sector,
            subsector=obj.subsector,
            segment=obj.segment,
            listing=obj.listing,
            activity=obj.activity,
            registrar=obj.registrar,
            website=obj.website,

            company_type=obj.company_type,
            status=obj.status,
            b3_code=obj.b3_code,
            company_category=obj.company_category,
            corporate_name=obj.corporate_name,
            registration_date=obj.registration_date,
            start_situation_date=obj.start_situation_date,
            situation=obj.situation,
            situation_date=obj.situation_date,
            country=obj.country,
            state=obj.state,
            city=obj.city,

        )

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

