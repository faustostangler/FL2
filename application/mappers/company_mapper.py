from __future__ import annotations

from infrastructure.helpers.data_cleaner import DataCleaner
from domain.dto import (
    BseCompanyDTO,
    DetailCompanyDTO,
    CompanyDTO,
)


class CompanyMapper:
    """Merge base and detail company data into a parsed DTO."""

    def __init__(self, data_cleaner: DataCleaner):
        self.data_cleaner = data_cleaner

    def merge_company_dtos(
        self,
        base: BseCompanyDTO,
        detail: DetailCompanyDTO,
    ) -> CompanyDTO:
        codes = detail.other_codes
        ticker_codes = [c.code for c in codes if c.code]
        isin_codes = [c.isin for c in codes if c.isin]

        industry = detail.industry_classification or ""
        parts = [p.strip() for p in industry.split("/")]

        ticker = self.data_cleaner.clean_text(base.issuing_company)
        company_name = self.data_cleaner.clean_text(base.company_name)
        cvm_code = self.data_cleaner.clean_text(base.cvm_code)
        cnpj = self.data_cleaner.clean_text(detail.cnpj)
        trading_name = self.data_cleaner.clean_text(detail.trading_name)
        listing = self.data_cleaner.clean_text(detail.listing_segment)
        registrar = self.data_cleaner.clean_text(detail.registrar)
        website = detail.website
        sector = self.data_cleaner.clean_text(parts[0]) if len(parts) > 0 else None
        subsector = (
            self.data_cleaner.clean_text(parts[1]) if len(parts) > 1 else None
        )
        segment = self.data_cleaner.clean_text(parts[2]) if len(parts) > 2 else None

        market_indicator = self.data_cleaner.clean_text(
            base.market_indicator or detail.market_indicator
        )
        bdr_type = self.data_cleaner.clean_text(base.type_bdr or detail.type_bdr)
        listing_date = self.data_cleaner.clean_date(base.listing_date)
        status = self.data_cleaner.clean_text(base.status or detail.status)
        segment_b3 = self.data_cleaner.clean_text(base.segment_b3)
        segment_eng = self.data_cleaner.clean_text(base.segment_eng)
        company_type = self.data_cleaner.clean_text(base.company_type)
        market = self.data_cleaner.clean_text(base.market or detail.market)
        industry_classification = detail.industry_classification
        industry_classification_eng = detail.industry_classification_eng
        activity = detail.activity
        institution_common = self.data_cleaner.clean_text(detail.institution_common)
        institution_preferred = self.data_cleaner.clean_text(
            detail.institution_preferred
        )
        last_date = self.data_cleaner.clean_date(detail.last_date)
        describle_category_bvmf = self.data_cleaner.clean_text(
            detail.describle_category_bvmf
        )
        quotation_date = self.data_cleaner.clean_date(detail.date_quotation)

        return CompanyDTO(
            ticker=ticker,
            company_name=company_name,
            cvm_code=cvm_code,
            cnpj=cnpj,
            trading_name=trading_name,
            listing=listing,
            registrar=registrar,
            website=website,
            ticker_codes=ticker_codes,
            isin_codes=isin_codes,
            other_codes=codes,
            sector=sector,
            subsector=subsector,
            segment=segment,
            market_indicator=market_indicator,
            bdr_type=bdr_type,
            listing_date=listing_date,
            status=status,
            segment_b3=segment_b3,
            segment_eng=segment_eng,
            company_type=company_type,
            market=market,
            industry_classification=industry_classification,
            industry_classification_eng=industry_classification_eng,
            activity=activity,
            has_quotation=detail.has_quotation,
            institution_common=institution_common,
            institution_preferred=institution_preferred,
            last_date=last_date,
            has_emissions=detail.has_emissions,
            has_bdr=detail.has_bdr,
            describle_category_bvmf=describle_category_bvmf,
            quotation_date=quotation_date,
        )
