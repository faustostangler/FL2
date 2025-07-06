"""Processors for cleaning and merging company data."""

from __future__ import annotations

import base64
import json
from typing import Dict, List, Optional, Type, Union, cast

from application import CompanyMapper
from domain.dto import CompanyDetailDTO, CompanyListingDTO, CompanyRawDTO
from domain.ports import LoggerPort, MetricsCollectorPort
from infrastructure.helpers import FetchUtils
from infrastructure.helpers.data_cleaner import DataCleaner


class EntryCleaner:
    """Clean raw company listing entries."""

    def __init__(self, data_cleaner: DataCleaner) -> None:
        """Initialize with ``DataCleaner``."""
        self.data_cleaner = data_cleaner

    def run(
            self,
            entry: Dict,
            text_keys: List[str],
            date_keys: List[str],
            number_keys: Optional[List[str]],
            dto_class: Type[Union[CompanyListingDTO, CompanyDetailDTO]],
            ) -> Union[CompanyListingDTO, CompanyDetailDTO]:
        """Return a ``CompanyListingDTO`` from the given entry."""
        cleaned = self.data_cleaner.clean_dict_fields(entry, text_keys, date_keys, number_keys)
        return dto_class.from_dict(cleaned)



class DetailFetcher:
    """Fetch and clean detailed company information."""

    def __init__(
        self,
        fetch_utils: FetchUtils,
        session,
        endpoint_detail: str,
        language: str,
        metrics_collector: MetricsCollectorPort,
        data_cleaner: DataCleaner,
    ) -> None:
        """Store HTTP utilities and configuration."""
        self.fetch_utils = fetch_utils
        self.session = session
        self.endpoint_detail = endpoint_detail
        self.language = language
        self.metrics_collector = metrics_collector
        self.data_cleaner = data_cleaner

    def run(self, cvm_code: str) -> Dict:
        """Fetch detail JSON and normalize fields."""
        payload = {"codeCVM": cvm_code, "language": self.language}
        token = base64.b64encode(json.dumps(payload).encode("utf-8")).decode("utf-8")
        url = self.endpoint_detail + token
        response, self.session = self.fetch_utils.fetch_with_retry(self.session, url)
        self.metrics_collector.record_network_bytes(len(response.content))
        raw = response.json()
        return raw


class CompanyMerger:
    """Merge base and detail DTOs."""

    def __init__(self, mapper: CompanyMapper, logger: LoggerPort) -> None:
        """Store mapper and logger."""
        self.mapper = mapper
        self.logger = logger

        self.logger.log(f"Load Class {self.__class__.__name__}", level="info")

    def run(
        self, listing: CompanyListingDTO, detail: CompanyDetailDTO
    ) -> Optional[CompanyRawDTO]:
        """Merge listing and detail DTOs into a raw DTO."""
        try:
            return self.mapper.merge_company_dtos(listing, detail)
        except Exception as exc:  # noqa: BLE001
            self.logger.log(f"erro {exc}", level="debug")
            return None


class CompanyDetailProcessor:
    """Pipeline to process a single company entry."""

    def __init__(
        self, cleaner: EntryCleaner, fetcher: DetailFetcher, merger: CompanyMerger
    ) -> None:
        """Store dependencies used to process a company entry."""
        self.cleaner = cleaner
        self.fetcher = fetcher
        self.merger = merger

    def run(self, entry: Dict) -> Optional[CompanyRawDTO]:
        """Clean, fetch details, and merge into a raw DTO."""
        try:
            text_keys=[
                "issuingCompany",
                "companyName",
                "tradingName",
                "segment",
                "segmentEng",
                "market",
            ]
            date_keys=["dateListing"]
            number_keys = []
            listing = cast(CompanyListingDTO, self.cleaner.run(entry=entry, text_keys=text_keys, date_keys=date_keys, number_keys=number_keys, dto_class=CompanyListingDTO))

            detail = self.fetcher.run(str(listing.cvm_code))
            text_keys=[
                "issuingCompany",
                "companyName",
                "tradingName",
                "IndustryClassificationEng",
                "market",
                "institutionCommon",
                "institutionPreferred",
                "market",
                "institutionCommon",
                "institutionPreffered",
                ]
            date_keys=["lastDate", "dateQuotation"]
            number_keys = []
            detail = cast(CompanyDetailDTO, self.cleaner.run(entry=detail, text_keys=text_keys, date_keys=date_keys, number_keys=number_keys, dto_class=CompanyDetailDTO))

            return self.merger.run(listing, detail)
        except Exception:
            pass
