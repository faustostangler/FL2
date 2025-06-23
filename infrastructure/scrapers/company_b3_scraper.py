from typing import Callable, Dict, List, Optional, Set

import base64
import json
import time
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
import threading


from infrastructure.config import Config
from infrastructure.logging import Logger
from infrastructure.helpers import FetchUtils
from infrastructure.helpers.data_cleaner import DataCleaner


class CompanyB3Scraper:
    """
    Scraper adapter responsible for fetching raw company data.
    In a real implementation, this could use requests, BeautifulSoup, or Selenium.
    """

    def __init__(self, config: Config, logger: Logger, data_cleaner: DataCleaner):
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

        # Log the initialization of the CompanyB3Scraper
        self.logger.log("Start CompanyB3Scraper", level="info")

        # Initialize FetchUtils for HTTP request utilities
        self.fetch_utils = FetchUtils(config, logger)

        # Set language and API company_endpoint from configuration
        self.language = config.b3.language
        self.endpoint_companies_list = config.b3.company_endpoint["initial"]
        self.endpoint_detail = config.b3.company_endpoint["detail"]
        self.endpoint_financial = config.b3.company_endpoint["financial"]

        # Initialize a cloudscraper session for HTTP requests
        self.session = self.fetch_utils.create_scraper()

    def fetch_all(
        self,
        threshold: Optional[int] = None,
        skip_codes: Optional[Set[str]] = None,
        save_callback: Optional[Callable[[List[dict]], None]] = None,
        max_workers: int | None = None,
    ) -> List[Dict]:
        """Fetch all companies from B3.

        Args:
            threshold: Number of companies to buffer before saving.
            skip_codes: CVM codes to ignore.
            save_callback: Optional callback to persist partial results.
            max_workers: Optional thread count for future parallelism.

        Returns:
            List of dictionaries representing raw company data.
        """
        # Ensure skip_codes is a set (to avoid None and allow fast lookup)
        skip_codes = skip_codes or set()
        # Determine the save threshold (number of companies before saving buffer)
        threshold = threshold or self.config.global_settings.threshold or 50

        # Fetch the initial list of companies from B3, possibly skipping some CVM codes
        companies_list = self._fetch_companies_list(skip_codes, threshold)
        # Fetch and parse detailed information for each company, with optional skipping and periodic saving
        companies = self._fetch_companies_details(
            companies_list,
            skip_codes,
            save_callback,
            threshold,
            max_workers,
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
        # Set initial pagination parameters
        self.logger.log("Get Existing Companies from B3", level="info")

        results = []
        start_time = time.time()

        # Loop through all pages of company data
        while True:
            # Build the payload for the current page
            payload = {
                "language": self.language,
                "pageNumber": self.PAGE_NUMBER,
                "pageSize": self.PAGE_SIZE,
            }
            # Encode the payload as required by the B3 API
            token = self._encode_payload(payload)
            url = self.endpoint_companies_list + token

            # Fetch the current page of results with retry logic
            response = self.fetch_utils.fetch_with_retry(self.session, url)
            data = response.json()

            # Extract and accumulate results from the current page
            current_results = data.get("results", [])
            results.extend(current_results)

            # Determine the total number of pages from the response
            total_pages = data.get("page", {}).get("totalPages", 1)

            # Log progress for monitoring
            progress = {
                "index": self.PAGE_NUMBER - 1,
                "size": total_pages,
                "start_time": start_time,
            }
            self.logger.log(
                f"{self.PAGE_NUMBER}/{total_pages}", level="info", progress=progress
            )

            # Check if all pages have been processed
            if self.PAGE_NUMBER >= total_pages:
                break

            # Move to the next page
            self.PAGE_NUMBER += 1

        # Return the complete list of companies
        return results

    def _encode_payload(self, payload: dict) -> str:
        """
        Codifica um dicionário JSON para o formato base64 usado pela B3.

        :param payload: Dicionário de entrada
        :return: String base64
        """
        return base64.b64encode(json.dumps(payload).encode("utf-8")).decode("utf-8")

    def _fetch_companies_details(
        self,
        companies_list: List[Dict],
        skip_codes: Optional[Set[str]] = None,
        save_callback: Optional[Callable[[List[dict]], None]] = None,
        threshold: Optional[int] = None,
        max_workers: int | None = None,
    ) -> List[Dict]:
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

        self.logger.log("Start CompanyB3Scraper fetch_all", level="info")
        start_time = time.time()

        if (max_workers or 1) <= 1:
            return self._fetch_companies_details_single(
                companies_list,
                skip_codes,
                save_callback,
                threshold,
                start_time,
            )

        return self._fetch_companies_details_threaded(
            companies_list,
            skip_codes,
            save_callback,
            threshold,
            max_workers or 1,
            start_time,
        )

    def _fetch_detail(self, cvm_code: str) -> Dict:
        """
        Busca os detalhes de uma empresa a partir do código CVM.

        :param cvm_code: Código CVM da empresa
        :return: Dicionário com detalhes estendidos da empresa
        """
        # Prepare the payload with the CVM code and language for the request
        payload = {"codeCVM": cvm_code, "language": self.language}
        # Encode the payload as base64 to match B3 API requirements
        token = self._encode_payload(payload)
        # Build the full URL for the detail endpoint
        url = self.endpoint_detail + token
        # Fetch the company detail data with retry logic
        response = self.fetch_utils.fetch_with_retry(self.session, url)
        # Return the parsed JSON response
        return response.json()

    def _parse_company(self, base: Dict, detail: Dict) -> Optional[Dict]:
        """
        Combina os dados do resultado base com os detalhes e retorna um dicionário padronizado.

        :param base: Dados iniciais da empresa (Getcompanies_listCompanies)
        :param detail: Detalhes adicionais da empresa (GetDetail)
        :return: Dicionário padronizado
        """
        try:
            # Extract and clean company fields from base and detail data
            codes = detail.get("otherCodes", []) or []
            ticker_codes = [c["code"] for c in codes if "code" in c]
            isin_codes = [c["isin"] for c in codes if "isin" in c]

            # Classificação setorial
            industry = detail.get("industryClassification", "")
            parts = [p.strip() for p in industry.split("/")]

            ticker = self.data_cleaner.clean_text(base.get("issuingCompany"))
            company_name = self.data_cleaner.clean_text(base.get("companyName"))
            cvm_code = self.data_cleaner.clean_text(base.get("codeCVM"))
            cnpj = self.data_cleaner.clean_text(detail.get("cnpj"))
            trading_name = self.data_cleaner.clean_text(detail.get("tradingName"))
            listing = self.data_cleaner.clean_text(detail.get("listingSegment"))
            registrar = self.data_cleaner.clean_text(detail.get("registrar"))
            website = detail.get("website")
            sector = self.data_cleaner.clean_text(parts[0]) if len(parts) > 0 else None
            subsector = (
                self.data_cleaner.clean_text(parts[1]) if len(parts) > 1 else None
            )
            segment = self.data_cleaner.clean_text(parts[2]) if len(parts) > 2 else None

            market_indicator = self.data_cleaner.clean_text(
                base.get("marketIndicator") or detail.get("marketIndicator")
            )
            type_bdr = self.data_cleaner.clean_text(
                base.get("typeBDR") or detail.get("typeBDR")
            )
            date_listing = self.data_cleaner.clean_date(base.get("dateListing"))
            status = self.data_cleaner.clean_text(
                base.get("status") or detail.get("status")
            )
            segment_b3 = self.data_cleaner.clean_text(base.get("segment"))
            segment_eng = self.data_cleaner.clean_text(base.get("segmentEng"))
            company_type = self.data_cleaner.clean_text(base.get("type"))
            market = self.data_cleaner.clean_text(
                base.get("market") or detail.get("market")
            )
            industry = detail.get("industryClassification")
            industry_eng = detail.get("industryClassificationEng")
            activity = detail.get("activity")
            institution_common = self.data_cleaner.clean_text(
                detail.get("institutionCommon")
            )
            institution_pref = self.data_cleaner.clean_text(
                detail.get("institutionPreferred")
            )
            last_date = self.data_cleaner.clean_date(detail.get("lastDate"))
            category = self.data_cleaner.clean_text(detail.get("describleCategoryBVMF"))
            quotation_date = self.data_cleaner.clean_date(detail.get("dateQuotation"))

            return {
                "ticker": ticker,
                "company_name": company_name,
                "cvm_code": cvm_code,
                "cnpj": cnpj,
                "trading_name": trading_name,
                "listing": listing,
                "registrar": registrar,
                "website": website,
                "ticker_codes": json.dumps(ticker_codes),
                "isin_codes": json.dumps(isin_codes),
                "otherCodes": codes,
                "sector": sector,
                "subsector": subsector,
                "segment": segment,
                "marketIndicator": market_indicator,
                "typeBDR": type_bdr,
                "dateListing": date_listing,
                "status": status,
                "segment_b3": segment_b3,
                "segmentEng": segment_eng,
                "type": company_type,
                "market": market,
                "industryClassification": industry,
                "industryClassificationEng": industry_eng,
                "activity": activity,
                "hasQuotation": detail.get("hasQuotation"),
                "institutionCommon": institution_common,
                "institutionPreferred": institution_pref,
                "lastDate": last_date,
                "hasEmissions": detail.get("hasEmissions"),
                "hasBDR": detail.get("hasBDR"),
                "describleCategoryBVMF": category,
                "dateQuotation": quotation_date,
            }
        except Exception as e:
            self.logger.log(f"erro {e}", level="debug")
            return None

    def _process_entry(
        self,
        index: int,
        entry: Dict,
        total_size: int,
        skip_codes: Set[str],
        start_time: float,
    ) -> Dict:
        entry["companyName"] = self.data_cleaner.clean_text(entry["companyName"])
        entry["issuingCompany"] = self.data_cleaner.clean_text(entry["issuingCompany"])
        entry["tradingName"] = self.data_cleaner.clean_text(entry["tradingName"])

        progress = {
            "index": index,
            "size": total_size,
            "start_time": start_time,
        }
        cvm_code = entry.get("codeCVM")
        extra_info = {
            "ticker": entry.get("issuingCompany"),
            "trading_name": entry.get("tradingName"),
            "company_name": entry.get("companyName"),
        }
        self.logger.log(
            f"{cvm_code} ", level="info", progress=progress, extra=extra_info
        )

        parsed = self._process_company_detail(entry, skip_codes)
        return {**entry, **(parsed or {})}

    def _fetch_companies_details_single(
        self,
        companies_list: List[Dict],
        skip_codes: Set[str],
        save_callback: Optional[Callable[[List[dict]], None]],
        threshold: int,
        start_time: float,
    ) -> List[Dict]:
        buffer: list[dict] = []
        results: list[dict] = []
        total_size = len(companies_list)

        for i, entry in enumerate(companies_list):
            processed = self._process_entry(
                i, entry, total_size, skip_codes, start_time
            )
            buffer.append(processed)
            results.append(processed)

            remaining_items = total_size - i - 1
            self._handle_save(
                buffer, results, save_callback, threshold, remaining_items
            )

        if buffer:
            self._handle_save(buffer, results, save_callback, threshold, 0)

        return results

    def _fetch_companies_details_threaded(
        self,
        companies_list: List[Dict],
        skip_codes: Set[str],
        save_callback: Optional[Callable[[List[dict]], None]],
        threshold: int,
        max_workers: int,
        start_time: float,
    ) -> List[Dict]:
        buffer: list[dict] = []
        results: list[dict] = []
        total_size = len(companies_list)

        task_queue: Queue = Queue(self.config.global_settings.queue_size)
        lock = threading.Lock()
        sentinel = object()

        def worker() -> None:
            while True:
                item = task_queue.get()
                if item is sentinel:
                    task_queue.task_done()
                    break
                index, entry = item
                processed = self._process_entry(
                    index, entry, total_size, skip_codes, start_time
                )
                with lock:
                    buffer.append(processed)
                    results.append(processed)
                    remaining_items = total_size - index - 1
                    self._handle_save(
                        buffer, results, save_callback, threshold, remaining_items
                    )
                task_queue.task_done()

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(worker) for _ in range(max_workers)]
            for index, entry in enumerate(companies_list):
                task_queue.put((index, entry))
            for _ in range(max_workers):
                task_queue.put(sentinel)
            task_queue.join()
            for future in futures:
                future.result()

        if buffer:
            self._handle_save(buffer, results, save_callback, threshold, 0)

        return results

    def _process_company_detail(
        self, entry: Dict, skip_codes: Set[str]
    ) -> Optional[Dict]:
        cvm_code = entry.get("codeCVM")
        if not cvm_code or cvm_code in skip_codes:
            return None
        try:
            detail = self._fetch_detail(str(cvm_code))
            return self._parse_company(entry, detail)
        except Exception as exc:  # noqa: BLE001
            self.logger.log(f"erro {exc}", level="warning")
            return None

    def _handle_save(
        self,
        buffer: List[Dict],
        results: Optional[List[dict]],
        save_callback: Optional[Callable[[List[dict]], None]],
        threshold: int,
        remaining_items: int,
    ) -> None:
        if (remaining_items % threshold == 0) or (remaining_items == 0):
            if callable(save_callback) and buffer:
                save_callback(buffer)
                self.logger.log(
                    f"Saved {len(buffer)} companies (partial)", level="info"
                )
                buffer.clear()
