from typing import Callable, Dict, List, Optional, Set, Tuple

import base64
import json
from dataclasses import asdict
import time
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
import threading
import uuid

from infrastructure.config import Config
from infrastructure.logging import Logger
from infrastructure.helpers import FetchUtils
from infrastructure.helpers.data_cleaner import DataCleaner
from infrastructure.helpers.byte_formatter import ByteFormatter
from domain.dto import (
    CodeDTO,
    RawBaseCompanyDTO,
    RawDetailCompanyDTO,
    RawParsedCompanyDTO,
)
from application import CompanyMapper


class CompanyB3Scraper:
    """
    Scraper adapter responsible for fetching raw company data.
    In a real implementation, this could use requests, BeautifulSoup, or Selenium.
    """

    def __init__(
        self,
        config: Config,
        logger: Logger,
        data_cleaner: DataCleaner,
        mapper: CompanyMapper,
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
        save_callback: Optional[Callable[[List[RawParsedCompanyDTO]], None]] = None,
        max_workers: int | None = None,
    ) -> List[RawParsedCompanyDTO]:
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
        # Set initial pagination parameters
        self.logger.log("Get Existing Companies from B3", level="info")

        download_bytes_execution_mode = 0
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
            download_bytes_item = len(response.content if response else b"")
            download_bytes_execution_mode += download_bytes_item
            self.download_bytes_total += download_bytes_item

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
            extra_info = {
                "download_global": self.byte_formatter.format_bytes(
                    self.download_bytes_total
                ),
                "download_total": self.byte_formatter.format_bytes(
                    download_bytes_execution_mode
                ),
                "download_bytes_item": self.byte_formatter.format_bytes(
                    download_bytes_item
                ),
            }
            self.logger.log(
                f"{self.PAGE_NUMBER}/{total_pages}",
                level="info",
                progress=progress,
                extra=extra_info,
            )

            # Check if all pages have been processed
            if self.PAGE_NUMBER >= total_pages:
                break

            # Move to the next page
            self.PAGE_NUMBER += 1

        self.logger.log(
            f"Global download: {self.byte_formatter.format_bytes(self.download_bytes_total)} | Total download: {self.byte_formatter.format_bytes(download_bytes_execution_mode)}",
            level="info",
        )

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
        save_callback: Optional[Callable[[List[RawParsedCompanyDTO]], None]] = None,
        threshold: Optional[int] = None,
        max_workers: int | None = None,
    ) -> Tuple[List[RawParsedCompanyDTO], int]:
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
        download_bytes_execution_mode = 0

        self.logger.log("Start CompanyB3Scraper fetch_all", level="info")
        start_time = time.time()

        if (max_workers or 1) <= 1:
            results, download_bytes_execution_mode = (
                self._fetch_companies_details_single(
                    companies_list,
                    skip_codes,
                    save_callback,
                    threshold,
                    start_time,
                )
            )
        results, download_bytes_execution_mode = self._fetch_companies_details_threaded(
            companies_list,
            skip_codes,
            save_callback,
            threshold,
            max_workers or 1,
            start_time,
        )

        return results, download_bytes_execution_mode

    def _fetch_detail(self, cvm_code: str) -> RawDetailCompanyDTO:
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
        response = self.fetch_utils.fetch_with_retry(self.session, url)
        self.download_bytes_total += len(response.content)

        return RawDetailCompanyDTO.from_dict(response.json())

    def _parse_company(
        self, base: RawBaseCompanyDTO, detail: RawDetailCompanyDTO
    ) -> Optional[RawParsedCompanyDTO]:
        """Merge base and detail DTOs into a parsed DTO."""

        try:
            return self.mapper.merge(base, detail)
        except Exception as e:  # noqa: BLE001
            self.logger.log(f"erro {e}", level="debug")
            return None

    def _process_entry(
        self,
        entry: Dict,
        skip_codes: Set[str],
    ) -> Optional[RawParsedCompanyDTO]:
        entry["companyName"] = self.data_cleaner.clean_text(entry["companyName"])
        entry["issuingCompany"] = self.data_cleaner.clean_text(entry["issuingCompany"])
        entry["tradingName"] = self.data_cleaner.clean_text(entry["tradingName"])

        base_dto = RawBaseCompanyDTO.from_dict(entry)

        parsed = self._process_company_detail(base_dto, skip_codes)

        return parsed

    def _fetch_companies_details_single(
        self,
        companies_list: List[Dict],
        skip_codes: Set[str],
        save_callback: Optional[Callable[[List[RawParsedCompanyDTO]], None]],
        threshold: int,
        start_time: float,
    ) -> Tuple[List[RawParsedCompanyDTO], int]:
        buffer: list[RawParsedCompanyDTO] = []
        results: list[RawParsedCompanyDTO] = []
        total_size = len(companies_list)
        download_bytes_execution_mode = 0

        for index, entry in enumerate(companies_list):
            ticker = entry["issuingCompany"]
            if ticker != "BBAS":
                continue

            cvm_code = entry.get("codeCVM")
            message = f"{cvm_code}"
            progress = {
                "index": index,
                "size": total_size,
                "start_time": start_time,
            }
            extra_info = {
                "issuing_company": entry.get("issuingCompany", ""),
                "company_name": entry.get("companyName", ""),
            }

            if cvm_code in skip_codes:
                self.logger.log(
                    message,
                    level="info",
                    progress=progress,
                    extra=extra_info,
                )

                continue

            processed = self._process_entry(entry, skip_codes)

            download_bytes_item = len(
                json.dumps(asdict(processed), default=str).encode("utf-8")
            )
            download_bytes_execution_mode += download_bytes_item
            self.download_bytes_total += download_bytes_item

            buffer.append(processed)
            results.append(processed)

            extra_info = {
                "issuing_company": entry.get("issuingCompany", ""),
                "company_name": entry.get("companyName", ""),
                "download_global": self.byte_formatter.format_bytes(
                    self.download_bytes_total
                ),
                "download_total": self.byte_formatter.format_bytes(
                    download_bytes_execution_mode
                ),
                "download_bytes_item": self.byte_formatter.format_bytes(
                    download_bytes_item
                ),
            }

            self.logger.log(
                message,
                level="info",
                progress=progress,
                extra=extra_info,
            )

            remaining_items = total_size - index - 1
            self._handle_save(
                buffer, results, save_callback, threshold, remaining_items
            )

        if buffer:
            self._handle_save(buffer, results, save_callback, threshold, 0)

        self.logger.log(
            f"Global download: {self.byte_formatter.format_bytes(self.download_bytes_total)} | Total download: {self.byte_formatter.format_bytes(download_bytes_execution_mode)}",
            level="info",
        )

        return results, download_bytes_execution_mode

    def _fetch_companies_details_threaded(
        self,
        companies_list: List[Dict],
        skip_codes: Set[str],
        save_callback: Optional[Callable[[List[RawParsedCompanyDTO]], None]],
        threshold: int,
        max_workers: int,
        start_time: float,
    ) -> Tuple[List[RawParsedCompanyDTO], int]:
        # ========== 1. Initialization ==========
        # Instantiate buffer and results lists to hold processed data
        buffer: list[RawParsedCompanyDTO] = []
        results: list[RawParsedCompanyDTO] = []

        # Calculate the total size of the companies list for progress tracking
        total_size = len(companies_list)

        # Create a thread-safe queue to distribute work tasks among threads
        task_queue: Queue = Queue(self.config.global_settings.queue_size)

        # Create a lock to synchronize and avoid concurrent access to shared resources
        lock = threading.Lock()

        #  Signal the end of processing for each worker
        sentinel = object()
        # self.logger.log("Queue Initialization", level="info")

        # ========== 2. Worker Function Definition ==========
        # Worker function to process entries from the queue
        def worker(worker_id: str) -> int:  # type: ignore
            # self.logger.log(f"Starting Worker {worker_id}", level="info")

            # Initialize variables
            download_bytes_worker = 0
            ticker = ""
            trading_name = ""

            # Continuously fetch items from the queue until a sentinel is received
            while True:
                # Block until an item is available and retrieve it from the queue
                # self.logger.log(f"Worker {worker_id} gets Queue Item {index} {cvm_code} {ticker} {trading_name}", level="info")
                item = task_queue.get()

                # If the item is the sentinel, mark the task as done and exit the loop
                if item is sentinel:
                    # self.logger.log(f"Queue Get Item {item} is sentinel {sentinel}", level="info")
                    task_queue.task_done()
                    return download_bytes_worker

                try:
                    index, entry = item

                    cvm_code = entry.get("codeCVM", "")
                    # company_name = entry.get("companyName", "")
                    ticker = entry.get("issuingCompany", "")
                    trading_name = entry.get("tradingName", "")

                    # Entry processing logic returning a processed dictionary
                    processed = self._process_entry(entry, skip_codes)

                    # Log the progress of processing (bytes downloaded for item, execcution and total)
                    download_bytes_item = len(
                        json.dumps(asdict(processed), default=str).encode("utf-8")
                    )
                    download_bytes_worker += download_bytes_item
                    self.download_bytes_total += download_bytes_item
                    # self.logger.log(f"Worker {worker_id} processed  Item {index} {cvm_code} {ticker} {trading_name} {self.byte_formatter.format_bytes(download_bytes_item)}", level="info")

                    # Add the processed entry to the buffer and results
                    with lock:
                        buffer.append(processed)
                        results.append(processed)

                        # Check if we need to save the current buffer
                        self.processed_count += 1
                        remaining_items = total_size - self.processed_count
                        # self.logger.log(f"Worker {worker_id} says remaining Items {remaining_items}", level="info")
                        self._handle_save(
                            buffer, results, save_callback, threshold, remaining_items
                        )

                        # Task is done, notify the queue
                        progress = {
                            "index": total_size - remaining_items - 1,
                            "size": total_size,
                            "start_time": start_time,
                        }
                        extra_info = {
                            "ticker": ticker,
                            "trading_name": trading_name,
                            "download_global": self.byte_formatter.format_bytes(
                                self.download_bytes_total
                            ),
                            # "download_total": self.byte_formatter.format_bytes(download_bytes_execution_mode),
                            "download_bytes_item": self.byte_formatter.format_bytes(
                                download_bytes_item
                            ),
                        }

                        self.logger.log(
                            f"{cvm_code}",
                            level="info",
                            progress=progress,
                            extra=extra_info,
                            worker_id=worker_id,
                        )

                except Exception as e:
                    self.logger.log(
                        f"Worker {worker_id} falhou em {ticker} {trading_name}: {e}",
                        level="warning",
                    )

                finally:
                    task_queue.task_done()

        # ========== 3. Thread Pool Execution ==========
        # Create a thread pool executor to manage worker threads
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # self.logger.log(f"Start ThreadPoolExecutor {executor._thread_name_prefix} threads:{executor._threads}", level="info")

            # Submit worker tasks to the executor. Each submit call returns a Future object containing the result of the worker function.
            # 1.1. range(max_workers) repeats for the number of max_workers
            # 1.2. worker is a thread (unit of execution) that processes tasks from a queue. worker task, in this case, is processing a company entry.
            # 2.1. list comprehension iterates over the range of max_workers, creating one Future for each worker.
            ## A future object is a placeholder for the worker's future result.
            # 2.2. executor.submit(worker) submits each worker function to the thread pool, the '_' is an unused placeholder for the loop variable.
            # 2.4. executor returns a future object representing the execution of the worker function.
            ## executor (ThreadPoolExecutor) is a (high-level) interface for managing a pool of threads asynchronously (simultaneously).
            ## A thread pool is a (high-level) collection of pre-instantiated worker threads that execute tasks from a queue, so multiple threads can run simultaneously.
            # 2. futures is a list of Future objects, each representing a worker thread that will process items from the task queue.
            # 3. The worker function will run in parallel, processing items from the task queue.
            # 4. The task queue will be filled with items to process, and each worker will pick up tasks from the queue, process them and store the results.

            # Stores the Future objects placeholders for the worker results
            # futures = [executor.submit(worker) for _ in range(max_workers)]
            futures = []
            for worker_index in range(max_workers):
                worker_id = uuid.uuid4().hex[:8]

                futures.append(executor.submit(worker, worker_id))
                # self.logger.log(f"Future executor submit worker {worker_id}", level="info")
            # executor.submit(worker) immediately calls/starts worker function in a separate asynchronous thread

            # ========== 4. Populate the Task Queue ==========
            # Populate the task queue with entries from the companies list and starts parallel processing
            for index, entry in enumerate(companies_list):
                # if index % 100 == 0:
                #     pass
                task_queue.put((index, entry))
                # self.logger.log(f"Task {index+1}/{total_size} in queue, total {task_queue.qsize()}", level="info")

            # ========== 5. Sentinel Objects ==========
            # Add sentinel objects to the queue to signal the end of processing for each worker
            for worker_id in range(max_workers):
                task_queue.put(sentinel)
                # self.logger.log(f"Sentinel in queue: {sentinel}", level="info")

            # ========== 6. Wait for Completion ==========
            # Wait for all tasks in the queue to be processed
            # self.logger.log("Wait for all tasks in the queue to be processed", level="info")
            task_queue.join()
            # self.logger.log("Join Done!", level="info")

            # Wait for all futures to complete and handle any exceptions, and sum up all bytes
            # # Inicializa o total em zero
            # download_bytes_execution_mode = 0

            # Para cada Future, aguarda o resultado e acumula
            # for future in futures:
            #     # future.result() bloqueia até a thread terminar e retorna o int de bytes baixados
            #     bytes_do_worker = future.result()
            #     download_bytes_execution_mode += bytes_do_worker
            download_bytes_execution_mode = sum(f.result() for f in futures)
            # self.logger.log(f"Future result {future}", level="info")

        # ========== 7. Finalization ==========
        # Final save
        if buffer:
            self.logger.log("Final buffer save", level="info")
            self._handle_save(buffer, results, save_callback, threshold, 0)

        # return aggregated results
        return results, download_bytes_execution_mode

    def _process_company_detail(
        self, base: RawBaseCompanyDTO, skip_codes: Set[str]
    ) -> Optional[RawParsedCompanyDTO]:
        try:
            cvm_code = base.cvm_code
            detail = self._fetch_detail(str(cvm_code))
            parsed = self._parse_company(base, detail)
            return parsed
        except Exception as exc:  # noqa: BLE001
            self.logger.log(f"erro {exc}", level="warning")
            return None

    def _handle_save(
        self,
        buffer: List[RawParsedCompanyDTO],
        results: Optional[List[RawParsedCompanyDTO]],
        save_callback: Optional[Callable[[List[RawParsedCompanyDTO]], None]],
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
