from __future__ import annotations

from datetime import datetime
from typing import List, Optional
import json

from sqlalchemy import Boolean, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from domain.dto.raw_company_dto import CodeDTO, RawCompanyDTO


class Base(DeclarativeBase):
    pass


class CompanyModel(Base):
    """ORM adapter for the ``tbl_company`` table."""

    __tablename__ = "tbl_company"

    cvm_code: Mapped[str] = mapped_column(primary_key=True)
    issuing_company: Mapped[Optional[str]] = mapped_column()
    trading_name: Mapped[Optional[str]] = mapped_column()
    company_name: Mapped[Optional[str]] = mapped_column()
    cnpj: Mapped[Optional[str]] = mapped_column()

    ticker_codes: Mapped[Optional[str]] = mapped_column()
    isin_codes: Mapped[Optional[str]] = mapped_column()
    other_codes: Mapped[Optional[str]] = mapped_column()

    industry_sector: Mapped[Optional[str]] = mapped_column()
    industry_subsector: Mapped[Optional[str]] = mapped_column()
    industry_segment: Mapped[Optional[str]] = mapped_column()
    industry_classification: Mapped[Optional[str]] = mapped_column()
    industry_classification_eng: Mapped[Optional[str]] = mapped_column()
    activity: Mapped[Optional[str]] = mapped_column()

    company_segment: Mapped[Optional[str]] = mapped_column()
    company_segment_eng: Mapped[Optional[str]] = mapped_column()
    company_category: Mapped[Optional[str]] = mapped_column()
    company_type: Mapped[Optional[str]] = mapped_column()

    listing_segment: Mapped[Optional[str]] = mapped_column()
    registrar: Mapped[Optional[str]] = mapped_column()
    website: Mapped[Optional[str]] = mapped_column()
    institution_common: Mapped[Optional[str]] = mapped_column()
    institution_preferred: Mapped[Optional[str]] = mapped_column()

    market: Mapped[Optional[str]] = mapped_column()
    status: Mapped[Optional[str]] = mapped_column()
    market_indicator: Mapped[Optional[str]] = mapped_column()

    code: Mapped[Optional[str]] = mapped_column()
    has_bdr: Mapped[Optional[bool]] = mapped_column(Boolean)
    type_bdr: Mapped[Optional[str]] = mapped_column()
    has_quotation: Mapped[Optional[bool]] = mapped_column(Boolean)
    has_emissions: Mapped[Optional[bool]] = mapped_column(Boolean)

    date_quotation: Mapped[Optional[datetime]] = mapped_column(DateTime)
    last_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    listing_date: Mapped[Optional[datetime]] = mapped_column(DateTime)

    @staticmethod
    def from_dto(dto: RawCompanyDTO) -> "CompanyModel":
        """Convert a :class:`RawCompanyDTO` into ``CompanyModel``."""

        return CompanyModel(
            cvm_code=dto.cvm_code or "",
            issuing_company=dto.issuing_company,
            trading_name=dto.trading_name,
            company_name=dto.company_name,
            cnpj=dto.cnpj,
            ticker_codes=",".join(dto.ticker_codes) if dto.ticker_codes else None,
            isin_codes=",".join(dto.isin_codes) if dto.isin_codes else None,
            other_codes=(
                json.dumps(
                    [{"code": code.code, "isin": code.isin} for code in dto.other_codes]
                )
                if dto.other_codes
                else None
            ),
            industry_sector=dto.industry_sector,
            industry_subsector=dto.industry_subsector,
            industry_segment=dto.industry_segment,
            industry_classification=dto.industry_classification,
            industry_classification_eng=dto.industry_classification_eng,
            activity=dto.activity,
            company_segment=dto.company_segment,
            company_segment_eng=dto.company_segment_eng,
            company_category=dto.company_category,
            company_type=dto.company_type,
            listing_segment=dto.listing_segment,
            registrar=dto.registrar,
            website=dto.website,
            institution_common=dto.institution_common,
            institution_preferred=dto.institution_preferred,
            market=dto.market,
            status=dto.status,
            market_indicator=dto.market_indicator,
            code=dto.code,
            has_bdr=dto.has_bdr,
            type_bdr=dto.type_bdr,
            has_quotation=dto.has_quotation,
            has_emissions=dto.has_emissions,
            date_quotation=dto.date_quotation,
            last_date=dto.last_date,
            listing_date=dto.listing_date,
        )

    def to_dto(self) -> RawCompanyDTO:
        """Reconstruct a :class:`RawCompanyDTO` from this model."""

        ticker_codes: List[str] = (
            self.ticker_codes.split(",") if self.ticker_codes else []
        )
        isin_codes: List[str] = self.isin_codes.split(",") if self.isin_codes else []
        raw_other = json.loads(self.other_codes) if self.other_codes else []
        other_codes = [
            CodeDTO(code=item.get("code"), isin=item.get("isin")) for item in raw_other
        ]

        return RawCompanyDTO(
            cvm_code=self.cvm_code,
            issuing_company=self.issuing_company,
            trading_name=self.trading_name,
            company_name=self.company_name,
            cnpj=self.cnpj,
            ticker_codes=ticker_codes,
            isin_codes=isin_codes,
            other_codes=other_codes,
            industry_sector=self.industry_sector,
            industry_subsector=self.industry_subsector,
            industry_segment=self.industry_segment,
            industry_classification=self.industry_classification,
            industry_classification_eng=self.industry_classification_eng,
            activity=self.activity,
            company_segment=self.company_segment,
            company_segment_eng=self.company_segment_eng,
            company_category=self.company_category,
            company_type=self.company_type,
            listing_segment=self.listing_segment,
            registrar=self.registrar,
            website=self.website,
            institution_common=self.institution_common,
            institution_preferred=self.institution_preferred,
            market=self.market,
            status=self.status,
            market_indicator=self.market_indicator,
            code=self.code,
            has_bdr=self.has_bdr,
            type_bdr=self.type_bdr,
            has_quotation=self.has_quotation,
            has_emissions=self.has_emissions,
            date_quotation=self.date_quotation,
            last_date=self.last_date,
            listing_date=self.listing_date,
        )
