"""Scraper implementation for fetching company data from the stock exchange."""

from __future__ import annotations

import base64
import json
import time
from typing import Callable, Dict, List, Optional, Set

from application import CompanyMapper
from domain.dto import CompanyRawDTO, ExecutionResultDTO, PageResultDTO, WorkerTaskDTO
from domain.ports import (
    CompanySourcePort,
    LoggerPort,
    MetricsCollectorPort,
    WorkerPoolPort,
)
from infrastructure.config import Config
from infrastructure.helpers import FetchUtils, SaveStrategy
from infrastructure.helpers.byte_formatter import ByteFormatter
from infrastructure.helpers.data_cleaner import DataCleaner
from infrastructure.scrapers.company_processors import (
    CompanyDetailProcessor,
    CompanyMerger,
    DetailFetcher,
    EntryCleaner,
)


class CompanyExchangeScraper(CompanySourcePort):
    """Scraper adapter responsible for fetching raw company data.

    In a real implementation, this could use requests, BeautifulSoup, or
    Selenium.
    """

    def __init__(
        self,
        config: Config,
        logger: LoggerPort,
        data_cleaner: DataCleaner,
        mapper: CompanyMapper,
        executor: WorkerPoolPort,
        metrics_collector: MetricsCollectorPort,
    ):
        """Set up configuration, logger and helper utilities for the scraper.

        Args:
            config (Config): Global configuration with exchange endpoints.
            logger (Logger): Logger used for progress and error messages.

        Attributes:
            config (Config): Stored configuration instance.
            logger (Logger): Stored logger instance.
            fetch_utils (FetchUtils): Utility for HTTP requests with retries.
            language (str): Language code for API requests.
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

        # Initialize FetchUtils for HTTP request utilities
        self.fetch_utils = FetchUtils(config, logger)

        # Set language and API company_endpoint from configuration
        self.language = config.exchange.language
        self.endpoint_companies_list = config.exchange.company_endpoint["initial"]
        self.endpoint_detail = config.exchange.company_endpoint["detail"]
        self.endpoint_financial = config.exchange.company_endpoint["financial"]

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

        # Log the initialization of the scraper
        self.logger.log("Start CompanyExchangeScraper", level="info")

    @property
    def metrics_collector(self) -> MetricsCollectorPort:
        """Metrics collector used by the scraper."""

        return self._metrics_collector

    def fetch_all(
        self,
        threshold: Optional[int] = None,
        skip_codes: Optional[Set[str]] = None,
        save_callback: Optional[Callable[[List[CompanyRawDTO]], None]] = None,
        max_workers: Optional[int] = None,
        **kwargs,
    ) -> ExecutionResultDTO[CompanyRawDTO]:
        """Fetch all companies from the exchange.

        Args:
            threshold: Number of companies to buffer before saving.
            skip_codes: CVM codes to ignore.
            save_callback: Optional callback to persist partial results.
            max_workers: Optional thread count for future parallelism.

        Returns:
            List of dictionaries representing raw company data.
        """
        self.logger.log("Start fetch_all", level="info")

        # Ensure skip_codes is a set (to avoid None and allow fast lookup)
        skip_codes = skip_codes or set()
        # Determine the save threshold (number of companies before saving buffer)
        threshold = threshold or self.config.global_settings.threshold or 50
        # Determine the number of simultaneous process
        max_workers = max_workers or self.config.global_settings.max_workers or 1

        # Fetch the initial list of companies, possibly skipping some CVM codes
        def noop(_buffer: List[Dict]) -> None:
            return None

        companies_list = self._fetch_companies_list(
            skip_codes=skip_codes,
            save_callback=noop,
            threshold=threshold,
            max_workers=max_workers,
        )

        # Fetch and parse detailed information for each company, with optional skipping and periodic saving
        companies = self._fetch_companies_details(
            companies_list=companies_list.items,
            skip_codes=skip_codes,
            save_callback=save_callback,
            threshold=threshold,
            max_workers=max_workers,
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
        max_workers: int | None = None,
    ) -> ExecutionResultDTO[Dict]:
        """Busca o conjunto inicial de empresas disponíveis na bolsa.

        :return: Lista de empresas com código CVM e nome base.
        """
        self.logger.log(
            "Start CompanyExchangeScraper fetch_companies_listing", level="info"
            )

        skip_codes = skip_codes or set()
        threshold = threshold or self.config.global_settings.threshold or 50
        max_workers = max_workers or self.config.global_settings.max_workers or 1

        strategy: SaveStrategy[Dict] = SaveStrategy(
            save_callback, threshold, config=self.config
        )
        page_exec = ExecutionResultDTO(
            items=[], metrics=self.metrics_collector.get_metrics(0)
        )
        fetch = PageResultDTO(items=[], total_pages=0, bytes_downloaded=0)
        results = []

        start_time = time.perf_counter()

        page = 1

        download_bytes_pre = self._metrics_collector.network_bytes
        fetch = self._fetch_page(page)
        download_bytes_pos = self._metrics_collector.network_bytes - download_bytes_pre

        total_pages = fetch.total_pages

        results = list(fetch.items)
        for item in fetch.items:
            strategy.handle(item)

        extra_info = {
            "Download": self.byte_formatter.format_bytes(download_bytes_pos),
            "Total download": self.byte_formatter.format_bytes(self.metrics_collector.network_bytes),
            }
        self.logger.log(
            f"Page {page}/{total_pages}",
            level="info",
            progress={
                "index": 0,
                "size": total_pages,
                "start_time": start_time,
            },
            extra=extra_info,
        )

        if total_pages > 1:
            tasks = list(enumerate(range(2, total_pages + 1)))

            def processor(task: WorkerTaskDTO) -> PageResultDTO:
                download_bytes_pre = self._metrics_collector.network_bytes
                fetch = self._fetch_page(task.data)
                download_bytes_pos = self._metrics_collector.network_bytes - download_bytes_pre

                extra_info = {
                    "Download": self.byte_formatter.format_bytes(download_bytes_pos),
                    "Total download": self.byte_formatter.format_bytes(self.metrics_collector.network_bytes),
                }
                self.logger.log(
                    f"Page {task.data}/{total_pages}",
                    level="info",
                    progress={
                        "index": task.index + 1,
                        "size": total_pages,
                        "start_time": start_time,
                    },
                    extra=extra_info,
                    worker_id=task.worker_id,
                )
                return fetch

            page_exec = self.executor.run(
                tasks=tasks,
                processor=processor,
                logger=self.logger,
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
        """Codifica um dicionário JSON para o formato base64 usado pela API.

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
        self.logger.log(
            "Start CompanyExchangeScraper fetch_companies_details", level="info"
        )

        skip_codes = skip_codes or set()
        threshold = threshold or self.config.global_settings.threshold or 50
        max_workers = max_workers or self.config.global_settings.max_workers or 1

        strategy: SaveStrategy[CompanyRawDTO] = SaveStrategy(
            save_callback, threshold, config=self.config
        )
        detail_exec: ExecutionResultDTO[Optional[CompanyRawDTO]] = ExecutionResultDTO(
            items=[], metrics=self.metrics_collector.get_metrics(0)
        )

        # Pair each company dict with its index for progress logging
        tasks = list(enumerate(companies_list))
        start_time = time.perf_counter()

        def processor(task: WorkerTaskDTO) -> Optional[CompanyRawDTO]:
            index = task.index
            entry = task.data
            worker_id = task.worker_id

            code_cvm = entry.get("codeCVM")
            if code_cvm in skip_codes:
                download_bytes_pre = self._metrics_collector.network_bytes
                download_bytes_pos = self._metrics_collector.network_bytes - download_bytes_pre

                # Log and skip already persisted companies
                extra_info = {
                "issuingCompany": entry["issuingCompany"],
                "trading_name": entry["tradingName"],
                "Download": self.byte_formatter.format_bytes(download_bytes_pos),
                "Total download": self.byte_formatter.format_bytes(self.metrics_collector.network_bytes),
                    }
                self.logger.log(
                    f"{code_cvm}",
                    level="info",
                    progress={
                        "index": index,
                        "size": len(tasks),
                        "start_time": start_time,
                    },
                    extra=extra_info,
                    worker_id=worker_id,
                )

                return None

            download_bytes_pre = self._metrics_collector.network_bytes
            result = self.detail_processor.run(entry)
            download_bytes_pos = self._metrics_collector.network_bytes - download_bytes_pre

            issuingCompany = entry.get("issuingCompany")
            tradingName = entry.get("tradingName")
            extra_info = {
                "issuingCompany": issuingCompany,
                "trading_name": tradingName,
                "Download": self.byte_formatter.format_bytes(download_bytes_pos),
                "Total download": self.byte_formatter.format_bytes(
                    self.metrics_collector.network_bytes
                ),
            }
            self.logger.log(
                f"{code_cvm}",
                level="info",
                progress={
                    "index": index,
                    "size": len(tasks),
                    "start_time": start_time,
                },
                extra=extra_info,
                worker_id=worker_id,
            )

            return result

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

