from typing import Callable, Dict, List, Optional, Set, Tuple

import base64
import json
from domain.ports import WorkerPoolPort

from infrastructure.config import Config
from infrastructure.logging import Logger
from infrastructure.helpers import FetchUtils
from infrastructure.helpers.byte_formatter import ByteFormatter

class CompanyB3Scraper:
    """
    Scraper adapter responsible for fetching raw company data.
    In a real implementation, this could use requests, BeautifulSoup, or Selenium.
    """

    def __init__(
        self,
        config: Config,
        logger: Logger,
        executor: WorkerPoolPort,
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
        self.executor = executor

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

        self.download_bytes_total = 0
        self.byte_formatter = ByteFormatter()

        # Initialize a counter for total processed items
        self.processed_count = 0

    def fetch_all(
        self,
        threshold: Optional[int] = None,
        skip_codes: Optional[Set[str]] = None,
        save_callback: Optional[Callable[[List[dict]], None]] = None,
        max_workers: int | None = None,
    ) -> List[dict]:
        """Fetch all companies from B3.

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

        # Fetch the initial list of companies from B3, possibly skipping some CVM codes
        companies_list = self._fetch_companies_list(skip_codes, threshold)
        # Fetch and parse detailed information for each company, with optional skipping and periodic saving
        companies, download_bytes_execution_mode = self._fetch_companies_details(
            companies_list,
            skip_codes,
            save_callback,
            threshold,
            max_workers,
        )

        self.logger.log(
            f"Global download: {self.byte_formatter.format_bytes(self.download_bytes_total)} | Total download: {self.byte_formatter.format_bytes(download_bytes_execution_mode)}",
            level="info",
        )

        # Return the complete list of parsed company details
        return companies

    def _fetch_companies_list(
        self, skip_codes: Optional[Set[str]] = None, threshold: Optional[int] = None
    ) -> List[Dict]:
        """
        Busca o conjunto inicial de empresas disponíveis na B3.

        :return: Lista de empresas com código CVM e nome base.
        """
        self.logger.log("Fetch Existing Companies from B3", level="info")

        first_page, total_pages, bytes_first = self._fetch_page(1)
        results = list(first_page)
        download_bytes_execution_mode = bytes_first

        if total_pages > 1:
            pages = list(range(2, total_pages + 1))
            tasks = list(enumerate(pages))
            self.logger.log("Fetch remaining company pages", level="info")

            def processor(item: Tuple[int, int]) -> Tuple[List[Dict], int, int]:
                _, page = item
                fetch = self._fetch_page(page)
                self.logger.log(
                    f"processor page {page} in _fetch_page",
                    level="info",
                )
                return fetch

            page_results, metrics = self.executor.run(
                tasks=tasks,
                processor=processor,
                logger=self.logger,
            )
            self.logger.log(
                "page_results done",
                level="info",
            )

            for page_data in page_results:
                page_items, _, bts = page_data
                self.logger.log(
                    f"page_data {bts}",
                    level="info",
                )
                results.extend(page_items)
                download_bytes_execution_mode += bts

        self.logger.log(
            f"Global download: {self.byte_formatter.format_bytes(self.download_bytes_total)} | Total download: {self.byte_formatter.format_bytes(download_bytes_execution_mode)}",
            level="info",
        )

        return results

    def _encode_payload(self, payload: dict) -> str:
        """
        Codifica um dicionário JSON para o formato base64 usado pela B3.

        :param payload: Dicionário de entrada
        :return: String base64
        """
        return base64.b64encode(json.dumps(payload).encode("utf-8")).decode("utf-8")

    def _fetch_page(self, page_number: int) -> Tuple[List[Dict], int, int]:
        payload = {
            "language": self.language,
            "pageNumber": page_number,
            "pageSize": self.PAGE_SIZE,
        }
        token = self._encode_payload(payload)
        url = self.endpoint_companies_list + token
        response = self.fetch_utils.fetch_with_retry(self.session, url)
        bytes_downloaded = len(response.content if response else b"")
        self.download_bytes_total += bytes_downloaded
        data = response.json()
        results = data.get("results", [])
        total_pages = data.get("page", {}).get("totalPages", 1)
        return results, total_pages, bytes_downloaded

    def _fetch_companies_details(
        self,
        companies_list: List[Dict],
        skip_codes: Optional[Set[str]] = None,
        save_callback: Optional[Callable[[List[dict]], None]] = None,
        threshold: Optional[int] = None,
        max_workers: int | None = None,
    ) -> Tuple[List[dict], int]:
        """
        Fetches and parses detailed information for a list of companies, with optional skipping and periodic saving.
        Args:
            companies_list (List[Dict]): List of company dictionaries, each containing at least a "codeCVM" key.
            skip_codes (Optional[Set[str]], optional): Set of CVM codes to skip during processing. Defaults to None.
            save_callback (Optional[Callable[[List[dict]], None]], optional): Callback function to save buffered company details periodically. Defaults to None.
            threshold (Optional[int], optional): Number of companies to process before triggering the save_callback. If not provided, uses configuration or defaults to 50.
            max_workers (int | None, optional): Reserved for future parallel fetching.
        Returns:
            List[Dict]: List of parsed company detail dictionaries.
        Logs:
            - Progress and status information at each step.
            - Warnings for any exceptions encountered during processing.
        Raises:
            - Does not raise exceptions; logs warnings instead.
        """

        threshold = threshold or self.config.global_settings.threshold or 50
        skip_codes = skip_codes or set()

        self.logger.log("Start CompanyB3Scraper fetch_companies_details", level="info")

        tasks = list(enumerate(companies_list))

        def processor(item: Tuple[int, Dict]) -> Optional[dict]:
            index, entry = item
            processed_entry = self._process_entry(entry, skip_codes)
            self.logger.log(f"Processor processed_entry {index}", level="info")

            return processed_entry

        buffer: List[dict] = []
        processed_results: List[dict] = []
        total_size = len(companies_list)

        def handle_batch(item: Optional[dict]) -> None:
            if item is None:
                return
            processed_results.append(item)
            buffer.append(item)
            remaining = total_size - len(processed_results)
            self._handle_save(
                buffer, processed_results, save_callback, threshold, remaining
            )

        results_out, metrics = self.executor.run(
            tasks=tasks,
            processor=processor,
            logger=self.logger,
            on_result=handle_batch,
        )
        self.logger.log("Processor processed_entry results", level="info")

        if buffer:
            self._handle_save(buffer, processed_results, save_callback, threshold, 0)

        self.download_bytes_total += metrics.download_bytes

        return results_out, metrics.download_bytes

    def _fetch_detail(self, cvm_code: str) -> dict:
        """
        Busca os detalhes de uma empresa a partir do código CVM.

        :param cvm_code: Código CVM da empresa
        :return: Raw dictionary returned by the API
        """
        self.logger.log("fetch company_detail", level="info")

        # Prepare the payload with the CVM code and language for the request
        payload = {"codeCVM": cvm_code, "language": self.language}
        # Encode the payload as base64 to match B3 API requirements
        token = self._encode_payload(payload)
        # Build the full URL for the detail endpoint
        url = self.endpoint_detail + token
        response = self.fetch_utils.fetch_with_retry(self.session, url)
        self.download_bytes_total += len(response.content)
        return response.json()


    def _process_entry(
        self,
        entry: Dict,
        skip_codes: Set[str],
    ) -> Optional[dict]:
        self.logger.log("Processor processing entry", level="info")

        return self._process_company_detail(entry, skip_codes)

    def _process_company_detail(
        self, base: Dict, skip_codes: Set[str]
    ) -> Optional[dict]:
        try:
            self.logger.log(
                "Parsing company_detail", level="info"
            )

            cvm_code = base.get("codeCVM")
            detail_raw = self._fetch_detail(str(cvm_code))
            return {"base": base, "detail": detail_raw}
        except Exception as exc:  # noqa: BLE001
            self.logger.log(f"erro {exc}", level="warning")
            return None

    def _handle_save(
        self,
        buffer: List[dict],
        results: Optional[List[dict]],
        save_callback: Optional[Callable[[List[dict]], None]],
        threshold: int,
        remaining_items: int,
    ) -> None:
        if (remaining_items % threshold == 0) or (remaining_items == 0):
            if callable(save_callback) and buffer:
                # self.logger.log(f"Remaining Items {remaining_items}", level="info")
                save_callback(buffer)
                self.logger.log(
                    f"Saved {len(buffer)} companies (partial)", level="info"
                )
                buffer.clear()
