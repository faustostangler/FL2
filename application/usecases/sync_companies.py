"""Use case for synchronizing company data between scraper and repository."""

import time
from typing import List

from domain.dto import SyncCompaniesResultDTO
from domain.dto.company_data_dto import CompanyDataDTO
from domain.dto.raw_company_data_dto import CompanyDataRawDTO
from domain.ports import CompanyDataScraperPort, LoggerPort, SqlAlchemyCompanyDataRepositoryPort
from infrastructure.helpers.list_flattener import ListFlattener


class SyncCompaniesUseCase:
    """Synchronize company data from the scraper to the repository."""

    def __init__(
        self,
        logger: LoggerPort,
        repository: SqlAlchemyCompanyDataRepositoryPort,
        scraper: CompanyDataScraperPort,
        max_workers: int = 1,
    ):
        """Store dependencies and configure use case execution."""
        self.logger = logger
        self.repository = repository
        self.scraper = scraper
        self.max_workers = max_workers

        # self.logger.log(f"Load Class {self.__class__.__name__}", level="info")

    def synchronize_companies(self) -> SyncCompaniesResultDTO:
        """Start the full synchronization pipeline.

        Steps:
            1. Fetch data from the scraper.
            2. Convert results into ``CompanyDataDTO`` objects.
            3. Persist them using the repository.
        """
        # self.logger.log("Run  Method sync_companies_usecase.run()", level="info")

        # Mark the start time to calculate performance metrics later.
        start = time.perf_counter()

        # Retrieve primary keys already stored to avoid reprocessing them.
        existing_company_codes = self.repository.get_all_primary_keys()

        # self.logger.log("Call Method sync_companies_usecase.run().fetch_all(save_callback, max_workers)", level="info")
        # Fetch all companies from the scraper and persist them batch-wise.
        results = self.scraper.fetch_all(
            skip_codes=existing_company_codes,
            save_callback=self._save_batch,
        )
        # self.logger.log("End  Method sync_companies_usecase.run().fetch_all(save_callback, max_workers)", level="info")

        # Measure download time and network usage.
        elapsed = time.perf_counter() - start
        bytes_downloaded = self.scraper.metrics_collector.network_bytes

        # self.logger.log("End  Method sync_companies_usecase.run()", level="info")

        return SyncCompaniesResultDTO(
            processed_count=len(results.items),
            skipped_count=len(existing_company_codes),
            bytes_downloaded=bytes_downloaded,
            elapsed_time=elapsed,
        )

    def _save_batch(self, buffer: List[CompanyDataRawDTO]) -> None:
        """Convert raw companies to domain DTOs before saving."""
        # primeiro “desembrulha” qualquer nível de listas aninhadas
        flat_items = ListFlattener.flatten(buffer)  # recebe nested lists, devolve flat list

        # Transform raw DTOs from the scraper to domain DTOs.
        dtos = [CompanyDataDTO.from_raw(item) for item in flat_items]

        # Persist the converted DTOs in bulk for efficiency.
        self.repository.save_all(dtos)

        # self.logger.log("End  Method _save_batch() in SyncCompaniesUseCase in CompanyDataService", level="info")
