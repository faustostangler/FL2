from dataclasses import dataclass
from typing import Optional
import json

from .raw_company_dto import CompanyRawDTO


@dataclass(frozen=True)
class CompanyDTO:
    """Representa os dados estruturados de uma empresa listada na B3."""

    cvm_code: Optional[str]
    company_name: Optional[str]
    ticker: Optional[str]  # Ticker é o código de negociação da ação na B3
    ticker_codes: Optional[str]
    isin_codes: Optional[str]
    trading_name: Optional[str]
    sector: Optional[str]
    subsector: Optional[str]
    segment: Optional[str]
    listing: Optional[str]
    activity: Optional[str]
    registrar: Optional[str]
    cnpj: Optional[str]
    website: Optional[str]

    company_type: Optional[str]
    status: Optional[str]
    company_category: Optional[str]
    corporate_name: Optional[str]
    listing_date: Optional[str]
    start_situation_date: Optional[str]
    situation: Optional[str]
    situation_date: Optional[str]
    country: Optional[str]
    state: Optional[str]
    city: Optional[str]

    @staticmethod
    def from_dict(raw: dict) -> "CompanyDTO":
        """
        Constrói um DTO imutável a partir de um dicionário bruto (normalmente vindo do scraper).
        """
        return CompanyDTO(
            cvm_code=raw.get("cvm_code") or raw.get("codeCVM"),
            company_name=raw.get("company_name") or raw.get("companyName"),
            ticker=raw.get("ticker") or raw.get("issuingCompany"),
            ticker_codes=raw.get("ticker_codes"),
            isin_codes=raw.get("isin_codes"),
            trading_name=raw.get("trading_name") or raw.get("tradingName"),
            sector=raw.get("sector"),
            subsector=raw.get("subsector"),
            segment=raw.get("segment"),
            listing=raw.get("listing"),
            activity=raw.get("activity"),
            registrar=raw.get("registrar"),
            cnpj=raw.get("cnpj"),
            website=raw.get("website"),
            company_type=raw.get("company_type"),
            status=raw.get("status"),
            company_category=raw.get("company_category"),
            corporate_name=raw.get("corporate_name"),
            listing_date=raw.get("listing_date"),
            start_situation_date=raw.get("start_situation_date"),
            situation=raw.get("situation"),
            situation_date=raw.get("situation_date"),
            country=raw.get("country"),
            state=raw.get("state"),
            city=raw.get("city"),
        )

    @staticmethod
    def from_raw(raw: CompanyRawDTO) -> "CompanyDTO":
        """Builds a CompanyDTO from a CompanyDTO instance."""

        return CompanyDTO(
            cvm_code=raw.cvm_code,
            company_name=raw.company_name,
            ticker=raw.ticker,
            ticker_codes=json.dumps(raw.ticker_codes) if raw.ticker_codes else None,
            isin_codes=json.dumps(raw.isin_codes) if raw.isin_codes else None,
            trading_name=raw.trading_name,
            sector=raw.sector,
            subsector=raw.subsector,
            segment=raw.industry_segment,
            listing=raw.listing,
            activity=raw.activity,
            registrar=raw.registrar,
            cnpj=raw.cnpj,
            website=raw.website,
            company_type=raw.company_type,
            status=raw.status,
            company_category=None,
            corporate_name=None,
            listing_date=(
                raw.listing_date.strftime("%Y-%m-%d") if raw.listing_date else None
            ),
            start_situation_date=None,
            situation=None,
            situation_date=None,
            country=None,
            state=None,
            city=None,
        )
