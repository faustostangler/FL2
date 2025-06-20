from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class CompanyDTO:
    """Representa os dados estruturados de uma empresa listada na B3."""

    cvm_code: Optional[str]
    company_name: str
    ticker: str
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
    b3_code: Optional[str]
    company_category: Optional[str]
    corporate_name: Optional[str]
    registration_date: Optional[str]
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
            cvm_code=raw.get("cvm_code"),
            company_name=raw["company_name"],
            ticker=raw["ticker"],
            ticker_codes=raw.get("ticker_codes"),
            isin_codes=raw.get("isin_codes"),
            trading_name=raw.get("trading_name"),
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
            b3_code=raw.get("b3_code"),
            company_category=raw.get("company_category"),
            corporate_name=raw.get("corporate_name"),
            registration_date=raw.get("registration_date"),
            start_situation_date=raw.get("start_situation_date"),
            situation=raw.get("situation"),
            situation_date=raw.get("situation_date"),
            country=raw.get("country"),
            state=raw.get("state"),
            city=raw.get("city"),
        )
