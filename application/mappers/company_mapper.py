import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("application > mappers > company_mapper.py")
from __future__ import annotations

from infrastructure.helpers.data_cleaner import DataCleaner
from domain.dto import (
    CompanyListingDTO,
    CompanyDetailDTO,
    CompanyRawDTO,
)


class CompanyMapper:
    """Merge base and detail company data into a parsed DTO."""
    import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("class CompantMapper")

    def __init__(self, data_cleaner: DataCleaner):
        import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("class CompantMapper __init__")
        self.data_cleaner = data_cleaner

    def merge_company_dtos(
        self,
        base: CompanyListingDTO,
        detail: CompanyDetailDTO,
    ) -> CompanyRawDTO:
        import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("class CompantMapper merge_company_dtos()")

        codes = detail.other_codes or []
        
        industry_classification = detail.industry_classification or ""
        parts = [p.strip() for p in industry_classification.split("/")]
        industry_sector = self.data_cleaner.clean_text(parts[0]) if len(parts) > 0 else None
        industry_subsector = self.data_cleaner.clean_text(parts[1]) if len(parts) > 1 else None
        industry_segment = self.data_cleaner.clean_text(parts[2]) if len(parts) > 2 else None

        return CompanyRawDTO(
            cvm_code = detail.cvm_code or base.cvm_code,
            issuing_company = detail.issuing_company or base.issuing_company,
            trading_name = detail.trading_name or base.trading_name,
            company_name = detail.company_name or base.company_name,
            cnpj = detail.cnpj or base.cnpj,

            ticker_codes = [c.code for c in codes if c.code],
            isin_codes = [c.isin for c in codes if c.isin],
            other_codes = codes,

            industry_sector = industry_sector, 
            industry_subsector = industry_subsector, 
            industry_segment = industry_segment,
            industry_classification = industry_classification,
            industry_classification_eng = detail.industry_classification_eng or None,
            activity = detail.activity or None,

            company_segment = base.segment or None, 
            company_segment_eng = base.segment_eng or None, 
            company_category = detail.company_category or None, 
            company_type = base.company_type or None, 

            listing_segment = detail.listing_segment or None, 
            registrar = detail.registrar or None, 
            website = detail.website or None, 
            institution_common = detail.institution_common or None, 
            institution_preferred = detail.institution_preferred or None, 
            
            market = detail.market or base.market, 
            status = detail.status or base.status, 
            market_indicator = detail.market_indicator or base.market_indicator, 

            code = detail.code or None, 
            has_bdr = detail.has_bdr or None, 
            type_bdr = detail.type_bdr or base.type_bdr, 
            has_quotation = detail.has_quotation or None, 
            has_emissions = detail.has_emissions or None, 

            date_quotation = detail.date_quotation or None, 
            last_date = detail.last_date, 
            listing_date = base.listing_date or "", 
        )
