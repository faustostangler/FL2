from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue
from threading import Thread
from typing import List, Dict

from infrastructure.config import Config
from infrastructure.logging import Logger
from infrastructure.repositories import SQLiteCompanyRepository
from infrastructure.scrapers.company_b3_scraper import CompanyB3Scraper
from domain.dto.company_dto import CompanyDTO


class MultiThreadedSyncCompaniesUseCase:
    """Synchronize companies using a producer/consumer threading model."""

    def __init__(
        self,
        config: Config,
        logger: Logger,
        repository: SQLiteCompanyRepository,
        scraper: CompanyB3Scraper,
    ) -> None:
        self.config = config
        self.logger = logger
        self.repository = repository
        self.scraper = scraper
        self.logger.log("Start MultiThreadedSyncCompaniesUseCase", level="info")

    def _fetch_and_parse(self, entry: Dict) -> Dict | None:
        cvm_code = entry.get("codeCVM")
        if not cvm_code:
            return None
        detail = self.scraper._fetch_detail(str(cvm_code))
        return self.scraper._parse_company(entry, detail)

    def execute(self) -> None:
        existing_codes = self.repository.get_all_primary_keys()
        companies_list = self.scraper._fetch_companies_list(skip_codes=existing_codes)

        queue: Queue[Dict | object] = Queue(
            maxsize=self.config.global_settings.queue_size
        )
        stop_token = object()

        def consumer() -> None:
            buffer: List[CompanyDTO] = []
            while True:
                item = queue.get()
                if item is stop_token:
                    if buffer:
                        self.repository.save_all(buffer)
                    queue.task_done()
                    break
                dto = CompanyDTO.from_dict(item)  # type: ignore[arg-type]
                buffer.append(dto)
                if len(buffer) >= self.config.global_settings.batch_size:
                    self.repository.save_all(buffer)
                    buffer.clear()
                queue.task_done()

        consumer_thread = Thread(target=consumer)
        consumer_thread.start()

        max_workers = self.config.global_settings.max_workers or 1
        futures = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for entry in companies_list:
                cvm_code = entry.get("codeCVM")
                if not cvm_code or cvm_code in existing_codes:
                    continue
                futures.append(executor.submit(self._fetch_and_parse, entry))
            for future in as_completed(futures):
                result = future.result()
                if result:
                    queue.put(result)

        queue.put(stop_token)
        queue.join()
        consumer_thread.join()
