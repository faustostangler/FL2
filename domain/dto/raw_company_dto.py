from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass(frozen=True)
class CodeDTO:
    """Represents a pair of ticker/ISIN codes."""

    code: Optional[str]
    isin: Optional[str]


@dataclass(frozen=True)
class RawParsedCompanyDTO:
    """Raw parsed data returned by the scraper before mapping to the domain."""

    ticker: Optional[str]
    company_name: Optional[str]
    cvm_code: Optional[str]
    cnpj: Optional[str]
    trading_name: Optional[str]
    listing: Optional[str]
    registrar: Optional[str]
    website: Optional[str]
    ticker_codes: List[str]
    isin_codes: List[str]
    other_codes: List[CodeDTO]
    sector: Optional[str]
    subsector: Optional[str]
    segment: Optional[str]
    market_indicator: Optional[str]
    bdr_type: Optional[str]
    listing_date: Optional[datetime]
    status: Optional[str]
    segment_b3: Optional[str]
    segment_eng: Optional[str]
    company_type: Optional[str]
    market: Optional[str]
    industry_classification: Optional[str]
    industry_classification_eng: Optional[str]
    activity: Optional[str]
    has_quotation: Optional[bool]
    institution_common: Optional[str]
    institution_preferred: Optional[str]
    last_date: Optional[datetime]
    has_emissions: Optional[bool]
    has_bdr: Optional[bool]
    describle_category_bvmf: Optional[str]
    quotation_date: Optional[datetime]
