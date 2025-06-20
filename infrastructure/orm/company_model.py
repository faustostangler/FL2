from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from typing import Optional
from domain.dto.company_dto import CompanyDTO
from infrastructure.config import Config

config = Config()

class Base(DeclarativeBase):
    pass

class CompanyModel(Base):
    """
    Modelo ORM da tabela de empresas no banco de dados.
    Serve como adaptador entre o domínio (DTO) e o banco (SQLAlchemy).
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

    @staticmethod
    def from_dto(dto: CompanyDTO) -> "CompanyModel":
        """
        Converte um CompanyDTO para um CompanyModel (para persistência).
        """
        return CompanyModel(
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
            city=dto.city
        )

    def to_dto(self) -> CompanyDTO:
        """
        Converte um CompanyModel em CompanyDTO (para lógica de domínio).
        """
        return CompanyDTO(
            ticker=self.ticker,
            company_name=self.company_name,
            cnpj=self.cnpj,
            cvm_code=self.cvm_code,
            ticker_codes=self.ticker_codes,
            isin_codes=self.isin_codes,
            trading_name=self.trading_name,
            sector=self.sector,
            subsector=self.subsector,
            segment=self.segment,
            listing=self.listing,
            activity=self.activity,
            registrar=self.registrar,
            website=self.website,
            
            company_type=self.company_type,
            status=self.status,
            b3_code=self.b3_code,
            company_category=self.company_category,
            corporate_name=self.corporate_name,
            registration_date=self.registration_date,
            start_situation_date=self.start_situation_date,
            situation=self.situation,
            situation_date=self.situation_date,
            country=self.country,
            state=self.state,
            city=self.city
        )
