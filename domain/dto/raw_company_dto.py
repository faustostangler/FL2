from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
import json


@dataclass(frozen=True)
class CodeDTO:
    """Represents a pair of ticker/ISIN codes."""

    code: Optional[str]
    isin: Optional[str]


@dataclass(frozen=True)
class BseCompanyDTO:
    """DTO for base company data from the list endpoint."""

    issuing_company: Optional[str]
    company_name: Optional[str]
    cvm_code: Optional[str]
    market_indicator: Optional[str]
    type_bdr: Optional[str]
    listing_date: Optional[str]
    status: Optional[str]
    segment_b3: Optional[str]
    segment_eng: Optional[str]
    company_type: Optional[str]
    market: Optional[str]

    @staticmethod
    def from_dict(raw: dict) -> "BseCompanyDTO":
        return BseCompanyDTO(
            issuing_company=raw.get("issuingCompany"),
            company_name=raw.get("companyName"),
            cvm_code=raw.get("codeCVM"),
            market_indicator=raw.get("marketIndicator"),
            type_bdr=raw.get("typeBDR"),
            listing_date=raw.get("dateListing"),
            status=raw.get("status"),
            segment_b3=raw.get("segment"),
            segment_eng=raw.get("segmentEng"),
            company_type=raw.get("type"),
            market=raw.get("market"),
        )


@dataclass(frozen=True)
class DetailCompanyDTO:
    """DTO for detailed company data from the detail endpoint."""

    cnpj: Optional[str]
    trading_name: Optional[str]
    listing_segment: Optional[str]
    registrar: Optional[str]
    website: Optional[str]
    other_codes: List[CodeDTO]
    market_indicator: Optional[str]
    type_bdr: Optional[str]
    status: Optional[str]
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
    date_quotation: Optional[datetime]

    @staticmethod
    def from_dict(raw: dict) -> "DetailCompanyDTO":
        codes = raw.get("otherCodes") or []
        if isinstance(codes, str):
            codes = json.loads(codes)
        code_dtos = [CodeDTO(code=c.get("code"), isin=c.get("isin")) for c in codes]
        return DetailCompanyDTO(
            cnpj=raw.get("cnpj"),
            trading_name=raw.get("tradingName"),
            listing_segment=raw.get("listingSegment"),
            registrar=raw.get("registrar"),
            website=raw.get("website"),
            other_codes=code_dtos,
            market_indicator=raw.get("marketIndicator"),
            type_bdr=raw.get("typeBDR"),
            status=raw.get("status"),
            market=raw.get("market"),
            industry_classification=raw.get("industryClassification"),
            industry_classification_eng=raw.get("industryClassificationEng"),
            activity=raw.get("activity"),
            has_quotation=raw.get("hasQuotation"),
            institution_common=raw.get("institutionCommon"),
            institution_preferred=raw.get("institutionPreferred"),
            last_date=raw.get("lastDate"),
            has_emissions=raw.get("hasEmissions"),
            has_bdr=raw.get("hasBDR"),
            describle_category_bvmf=raw.get("describleCategoryBVMF"),
            date_quotation=raw.get("dateQuotation"),
        )


@dataclass(frozen=True)
class CompanyDTO:
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
