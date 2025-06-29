from __future__ import annotations
import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("infrastructure > company_processors")

import base64
import json
from typing import Dict, Optional

from application import CompanyMapper
from domain.dto import CompanyDetailDTO, CompanyListingDTO, CompanyRawDTO
from infrastructure.helpers import FetchUtils, MetricsCollector
from infrastructure.helpers.data_cleaner import DataCleaner
from infrastructure.logging import Logger


class EntryCleaner:
    """Clean raw company listing entries."""
    import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("company_processors.EntryCleaner")

    def __init__(self, data_cleaner: DataCleaner) -> None:
        import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("EntryCleaner.__init__")
        self.data_cleaner = data_cleaner

    def run(self, entry: Dict) -> CompanyListingDTO:
        import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("EntryCleaner.run()")
        cleaned = self.data_cleaner.clean_company_entry(entry)
        return CompanyListingDTO.from_dict(cleaned)


#         entry["companyName"] = self.data_cleaner.clean_text(entry.get("companyName"))
#         entry["issuingCompany"] = self.data_cleaner.clean_text(
#             entry.get("issuingCompany")
#         )
#         entry["tradingName"] = self.data_cleaner.clean_text(entry.get("tradingName"))
#         entry["dateListing"] = self.data_cleaner.clean_date(entry.get("dateListing"))
#         return CompanyListingDTO.from_dict(entry)


class DetailFetcher:
    import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("company_processors.DetailFetcher")
    """Fetch and clean detailed company information."""

    def __init__(
        self,
        fetch_utils: FetchUtils,
        session,
        endpoint_detail: str,
        language: str,
        metrics_collector: MetricsCollector,
        data_cleaner: DataCleaner,
    ) -> None:
        import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("DetailFetcher.__init__")
        self.fetch_utils = fetch_utils
        self.session = session
        self.endpoint_detail = endpoint_detail
        self.language = language
        self.metrics_collector = metrics_collector
        self.data_cleaner = data_cleaner

    def run(self, cvm_code: str) -> CompanyDetailDTO:
        import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("DetailFetcher.run()")
        payload = {"codeCVM": cvm_code, "language": self.language}
        token = base64.b64encode(json.dumps(payload).encode("utf-8")).decode("utf-8")
        url = self.endpoint_detail + token
        response = self.fetch_utils.fetch_with_retry(self.session, url)
        self.metrics_collector.record_network_bytes(len(response.content))
        raw = response.json()
        raw["issuingCompany"] = self.data_cleaner.clean_text(raw.get("issuingCompany"))
        raw["companyName"] = self.data_cleaner.clean_text(raw.get("companyName"))
        raw["tradingName"] = self.data_cleaner.clean_text(raw.get("tradingName"))
        raw["cnpj"] = raw.get("cnpj")
        raw["industryClassification"] = raw.get("industryClassification")
        raw["industryClassificationEng"] = raw.get("industryClassificationEng")
        raw["activity"] = raw.get("activity")
        raw["website"] = raw.get("website")
        raw["hasQuotation"] = raw.get("hasQuotation")
        raw["status"] = raw.get("status")
        raw["marketIndicator"] = raw.get("marketIndicator")
        raw["market"] = self.data_cleaner.clean_text(raw.get("market"))
        raw["institutionCommon"] = self.data_cleaner.clean_text(
            raw.get("institutionCommon")
        )
        raw["institutionPreferred"] = self.data_cleaner.clean_text(
            raw.get("institutionPreferred")
        )
        raw["code"] = raw.get("code")
        raw["codeCVM"] = raw.get("codeCVM")
        raw["lastDate"] = self.data_cleaner.clean_date(raw.get("lastDate"))
        raw["otherCodes"] = raw.get("otherCodes")
        raw["hasEmissions"] = raw.get("hasEmissions")
        raw["hasBDR"] = raw.get("hasBDR")
        raw["typeBDR"] = raw.get("typeBDR")
        raw["describleCategoryBVMF"] = raw.get("describleCategoryBVMF")
        raw["dateQuotation"] = self.data_cleaner.clean_date(raw.get("dateQuotation"))
        return CompanyDetailDTO.from_dict(raw)


class CompanyMerger:
    """Merge base and detail DTOs."""
    import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("company_processors.CompanyMerger")

    def __init__(self, mapper: CompanyMapper, logger: Logger) -> None:
        import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("CompanyMerger.__init__")
        self.mapper = mapper
        self.logger = logger

    def run(
        self, base: CompanyListingDTO, detail: CompanyDetailDTO
    ) -> Optional[CompanyRawDTO]:
        import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("CompanyMerger.run()")
        try:
            return self.mapper.merge_company_dtos(base, detail)
        except Exception as exc:  # noqa: BLE001
            self.logger.log(f"erro {exc}", level="debug")
            return None


class CompanyDetailProcessor:
    """Pipeline to process a single company entry."""
    import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("company_processors.CompanyDetailProcessor")

    def __init__(
        self, cleaner: EntryCleaner, fetcher: DetailFetcher, merger: CompanyMerger
    ) -> None:
        import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("CompanyDetailProcessor.__init__")
        self.cleaner = cleaner
        self.fetcher = fetcher
        self.merger = merger

    def run(self, entry: Dict) -> Optional[CompanyRawDTO]:
        import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("CompanyDetailProcessor.run()")
        base = self.cleaner.run(entry)
        detail = self.fetcher.run(str(base.cvm_code))
        return self.merger.run(base, detail)
