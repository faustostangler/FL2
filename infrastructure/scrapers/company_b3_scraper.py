from __future__ import annotations

import base64
import json
from typing import Callable, Dict, List, Optional, Set, Tuple

from application import CompanyMapper
from domain.dto import CompanyRawDTO, ExecutionResultDTO, PageResultDTO
from domain.ports import (
    CompanySourcePort,
    MetricsCollectorPort,
    WorkerPoolPort,
)
from infrastructure.config import Config
from infrastructure.helpers import FetchUtils, SaveStrategy
from infrastructure.helpers.byte_formatter import ByteFormatter
from infrastructure.helpers.data_cleaner import DataCleaner
from infrastructure.logging import Logger
from infrastructure.scrapers.company_processors import (
    CompanyDetailProcessor,
    CompanyMerger,
    DetailFetcher,
    EntryCleaner,
)


class CompanyB3Scraper(CompanySourcePort):
    """Scraper adapter responsible for fetching raw company data.

    In a real implementation, this could use requests, BeautifulSoup, or
    Selenium.
    """

    def __init__(
        self,
        config: Config,
        logger: Logger,
        data_cleaner: DataCleaner,
        mapper: CompanyMapper,
        executor: WorkerPoolPort,
        metrics_collector: MetricsCollectorPort,
    ):
        """Set up configuration, logger and helper utilities for the scraper.

        Args:
            config (Config): Global configuration with B3 company_endpoint.
            logger (Logger): Logger used for progress and error messages.

        Attributes:
            config (Config): Stored configuration instance.
            logger (Logger): Stored logger instance.
            fetch_utils (FetchUtils): Utility for HTTP requests with retries.
            language (str): Language code for B3 API requests.
            endpoint_companies_list (str): URL for the companies list endpoint.
            endpoint_detail (str): URL for the company detail endpoint.
            endpoint_financial (str): URL for the financial data endpoint.
            session (requests.Session): Reusable HTTP session.

        Returns:
            None
        """

        # hardcoded parameters
        self.PAGE_NUMBER = 1
        self.PAGE_SIZE = 120

        # Store configuration and logger for use throughout the scraper
        self.config = config
        self.logger = logger
        self.data_cleaner = data_cleaner
        self.mapper = mapper
        self.executor = executor
        self._metrics_collector = metrics_collector

        # Log the initialization of the CompanyB3Scraper
        self.logger.log("Start CompanyB3Scraper", level="info")

        # Initialize FetchUtils for HTTP request utilities
        self.fetch_utils = FetchUtils(config, logger)

        # Set language and API company_endpoint from configuration
        self.language = config.b3.language
        self.endpoint_companies_list = config.b3.company_endpoint["initial"]
        self.endpoint_detail = config.b3.company_endpoint["detail"]
        self.endpoint_financial = config.b3.company_endpoint["financial"]

        # Initialize a requests session for HTTP requests
        self.session = self.fetch_utils.create_scraper()

        self.byte_formatter = ByteFormatter()

        # Initialize a counter for total processed items
        self.processed_count = 0

        self.entry_cleaner = EntryCleaner(self.data_cleaner)
        self.detail_fetcher = DetailFetcher(
            fetch_utils=self.fetch_utils,
            session=self.session,
            endpoint_detail=self.endpoint_detail,
            language=self.language,
            metrics_collector=self.metrics_collector,
            data_cleaner=self.data_cleaner,
        )
        self.company_merger = CompanyMerger(self.mapper, self.logger)
        self.detail_processor = CompanyDetailProcessor(
            cleaner=self.entry_cleaner,
            fetcher=self.detail_fetcher,
            merger=self.company_merger,
        )

    @property
    def metrics_collector(self) -> MetricsCollectorPort:
        """Metrics collector used by the scraper."""

        return self._metrics_collector

    def fetch_all(
        self,
        threshold: Optional[int] = None,
        skip_codes: Optional[Set[str]] = None,
        save_callback: Optional[Callable[[List[CompanyRawDTO]], None]] = None,
        max_workers: int | None = None,
    ) -> ExecutionResultDTO[CompanyRawDTO]:
        """Fetch all companies from B3.

        Args:
            threshold: Number of companies to buffer before saving.
            skip_codes: CVM codes to ignore.
            save_callback: Optional callback to persist partial results.
            max_workers: Optional thread count for future parallelism.

        Returns:
            List of dictionaries representing raw company data.
        """
        self.logger.log("Start (B3 Scraper) fetch_all", level="info")

        # Ensure skip_codes is a set (to avoid None and allow fast lookup)
        skip_codes = skip_codes or set()
        # Determine the save threshold (number of companies before saving buffer)
        threshold = threshold or self.config.global_settings.threshold or 50

        # Fetch the initial list of companies from B3, possibly skipping some CVM codes
        def noop(_buffer: List[Dict]) -> None:
            return None

        companies_list = self._fetch_companies_list(
            skip_codes, threshold, save_callback=noop
        )

        # Fetch and parse detailed information for each company, with optional skipping and periodic saving
        companies = self._fetch_companies_details(
            companies_list.items,
            skip_codes,
            save_callback,
            threshold,
            max_workers,
        )

        self.logger.log(
            f"Global download: {self.byte_formatter.format_bytes(self.metrics_collector.network_bytes)}",
            level="info",
        )

        # Return the complete list of parsed company details
        return companies

    def _fetch_companies_list(
        self,
        skip_codes: Optional[Set[str]] = None,
        threshold: Optional[int] = None,
        save_callback: Optional[Callable[[List[Dict]], None]] = None,
    ) -> ExecutionResultDTO[Dict]:
        """Busca o conjunto inicial de empresas disponíveis na B3.

        :return: Lista de empresas com código CVM e nome base.
        """
        self.logger.log("Fetch Existing Companies from B3", level="info")

        threshold = threshold or self.config.global_settings.threshold or 50
        strategy: SaveStrategy[Dict] = SaveStrategy(save_callback, threshold)
        page_exec = ExecutionResultDTO(
            items=[], metrics=self.metrics_collector.get_metrics(0)
        )

        first_page = self._fetch_page(1)
        results = list(first_page.items)
        for item in first_page.items:
            strategy.handle(item)
        total_pages = first_page.total_pages

        if total_pages > 1:
            tasks = list(enumerate(range(2, total_pages + 1)))

            def processor(task: Tuple[int, int]) -> PageResultDTO:
                _, page = task
                fetch = self._fetch_page(page)
                self.logger.log(
                    f"Fetching page {page}",
                    level="info",
                )
                return fetch

            page_exec = self.executor.run(
                tasks=tasks,
                processor=processor,
                logger=self.logger,
            )

            self.logger.log(
                "page_results done",
                level="info",
            )

            # Merge and flush each fetched page
            for page_data in page_exec.items:
                results.extend(page_data.items)

        strategy.finalize()

        self.logger.log(
            f"Global download: {self.byte_formatter.format_bytes(self.metrics_collector.network_bytes)}",
            level="info",
        )

        return ExecutionResultDTO(items=results, metrics=page_exec.metrics)

    def _encode_payload(self, payload: dict) -> str:
        """Codifica um dicionário JSON para o formato base64 usado pela B3.

        :param payload: Dicionário de entrada
        :return: String base64
        """

        return base64.b64encode(json.dumps(payload).encode("utf-8")).decode("utf-8")

    def _fetch_page(self, page_number: int) -> PageResultDTO:
        payload = {
            "language": self.language,
            "pageNumber": page_number,
            "pageSize": self.PAGE_SIZE,
        }
        token = self._encode_payload(payload)
        url = self.endpoint_companies_list + token
        response = self.fetch_utils.fetch_with_retry(self.session, url)
        bytes_downloaded = len(response.content if response else b"")
        self.metrics_collector.record_network_bytes(bytes_downloaded)
        data = response.json()
        results = data.get("results", [])
        total_pages = data.get("page", {}).get("totalPages", 1)
        return PageResultDTO(
            items=results,
            total_pages=total_pages,
            bytes_downloaded=bytes_downloaded,
        )

    def _fetch_companies_details(
        self,
        companies_list: List[Dict],
        skip_codes: Optional[Set[str]] = None,
        save_callback: Optional[Callable[[List[CompanyRawDTO]], None]] = None,
        threshold: Optional[int] = None,
        max_workers: int | None = None,
    ) -> ExecutionResultDTO[CompanyRawDTO]:
        """
        Fetches and parses detailed information for a list of companies, with optional skipping and periodic saving.
        Args:
            companies_list (List[Dict]): List of company dictionaries, each containing at least a "codeCVM" key.
            skip_codes (Optional[Set[str]], optional): Set of CVM codes to skip during processing. Defaults to None.
            save_callback (Optional[Callable[[List[CompanyRawDTO]], None]], optional):
                Callback function to save buffered company details periodically.
                Defaults to None.
            threshold (Optional[int], optional): Number of companies to process before triggering the save_callback. If not provided, uses configuration or defaults to 50.
            max_workers (int | None, optional): Reserved for future parallel fetching.
        Returns:
            ExecutionResultDTO[CompanyRawDTO]: Parsed company detail DTOs and
            execution metrics.
        Logs:
            - Progress and status information at each step.
            - Warnings for any exceptions encountered during processing.
        Raises:
            - Does not raise exceptions; logs warnings instead.
        """

        threshold = threshold or self.config.global_settings.threshold or 50
        skip_codes = skip_codes or set()
        strategy: SaveStrategy[CompanyRawDTO] = SaveStrategy(save_callback, threshold)
        detail_exec: ExecutionResultDTO[Optional[CompanyRawDTO]] = ExecutionResultDTO(
            items=[], metrics=self.metrics_collector.get_metrics(0)
        )

        self.logger.log("Start CompanyB3Scraper fetch_companies_details", level="info")

        # Pair each company dict with its index for progress logging
        tasks = list(enumerate(companies_list))

        def processor(item: Tuple[int, Dict]) -> Optional[CompanyRawDTO]:
            index, entry = item
            if entry.get("codeCVM") in skip_codes:
                # Skip already persisted companies
                return None

            processed_entry = self.detail_processor.run(entry)
            self.logger.log(f"Processor processed_entry {index}", level="info")

            return processed_entry

        def handle_batch(item: Optional[CompanyRawDTO]) -> None:
            # Buffer each parsed company and flush when threshold is hit
            strategy.handle(item)

        detail_exec = self.executor.run(
            tasks=tasks,
            processor=processor,
            logger=self.logger,
            on_result=handle_batch,
        )
        self.logger.log("Processor processed_entry results", level="info")

        strategy.finalize()

        results = [item for item in detail_exec.items if item is not None]

        return ExecutionResultDTO(items=results, metrics=detail_exec.metrics)
