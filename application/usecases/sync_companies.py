import time
from typing import List

from domain.dto import SyncCompaniesResultDTO
from domain.dto.company_dto import CompanyDTO
from domain.dto.raw_company_dto import CompanyRawDTO
from domain.ports import CompanyRepositoryPort, CompanySourcePort, LoggerPort


class SyncCompaniesUseCase:
    """Use case for synchronizing company data from the scraper to the
    repository."""

    def __init__(
        self,
        logger: LoggerPort,
        repository: CompanyRepositoryPort,
        scraper: CompanySourcePort,
        max_workers: int,
    ):
        """Store dependencies and configure use case execution."""
        self.logger = logger
        # Emit a log entry to signal the use case was created.
        self.logger.log("Start SyncCompaniesUseCase", level="info")

        # Keep references to infrastructure components.
        self.repository = repository
        self.scraper = scraper
        self.max_workers = max_workers

    def execute(self) -> SyncCompaniesResultDTO:
        """Run the full synchronization pipeline.

        Steps:
            1. Fetch data from the scraper.
            2. Convert results into ``CompanyDTO`` objects.
            3. Persist them using the repository.
        """
        self.logger.log("Start SyncCompaniesUseCase (B3 Scraper) Execute", level="info")

        # Mark the start time to calculate performance metrics later.
        start = time.perf_counter()

        # Retrieve primary keys already stored to avoid reprocessing them.
        existing_codes = self.repository.get_all_primary_keys()

        # Fetch all companies from the scraper and persist them batch-wise.
        results = self.scraper.fetch_all(
            skip_codes=existing_codes,
            save_callback=self._save_batch,
            max_workers=self.max_workers,
        )

        # Measure download time and network usage.
        elapsed = time.perf_counter() - start
        bytes_downloaded = self.scraper.metrics_collector.network_bytes
        self.logger.log(
            f"Downloaded {bytes_downloaded} bytes in {elapsed:.2f}s",
            level="info",
        )

        return SyncCompaniesResultDTO(
            processed_count=len(results),
            skipped_count=len(existing_codes),
            bytes_downloaded=bytes_downloaded,
            elapsed_time=elapsed,
        )

    def _save_batch(self, buffer: List[CompanyRawDTO]) -> None:
        """Convert raw companies to domain DTOs before saving."""
        # # Debug log for observability of background execution.
        # self.logger.log("SyncCompaniesUseCase _save_batch", level="info")

        # Transform raw DTOs from the scraper to domain DTOs.
        dtos = [CompanyDTO.from_raw(item) for item in buffer]

        # Persist the converted DTOs in bulk for efficiency.
        self.repository.save_all(dtos)
