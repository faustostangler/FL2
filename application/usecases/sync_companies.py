import time
from typing import List

from domain.dto import SyncCompaniesResultDTO
from domain.dto.company_dto import CompanyDTO
from domain.dto.raw_company_dto import CompanyRawDTO
from domain.ports import CompanyRepositoryPort, CompanySourcePort
from infrastructure.logging import Logger


class SyncCompaniesUseCase:
    """Use case for synchronizing company data from the scraper to the repository."""
    def __init__(
        self,
        logger: Logger,
        repository: CompanyRepositoryPort,
        scraper: CompanySourcePort,
        max_workers: int,
    ):
        """Store dependencies and configure use case execution."""
        self.logger = logger
        self.logger.log("Start SyncCompaniesUseCase", level="info")

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
        self.logger.log("SyncCompaniesUseCase Execute", level="info")

        start = time.perf_counter()
        existing_codes = self.repository.get_all_primary_keys()

        results = self.scraper.fetch_all(
            skip_codes=existing_codes,
            save_callback=self._save_batch,
            max_workers=self.max_workers,
        )
        elapsed = time.perf_counter() - start
        bytes_downloaded = self.scraper.metrics_collector.network_bytes
        self.logger.log(
            f"Downloaded {bytes_downloaded} bytes",
            level="info",
        )

#         return SyncCompaniesResultDTO(
#             processed_count=len(results),
#             skipped_count=len(existing_codes),
#             bytes_downloaded=bytes_downloaded,
#             elapsed_time=elapsed,
#         )

    def _save_batch(self, buffer: List[CompanyRawDTO]) -> None:
        """Convert raw companies to domain DTOs before saving."""
        self.logger.log("SyncCompaniesUseCase _save_batch", level="info")

        dtos = [CompanyDTO.from_raw(item) for item in buffer]
        self.repository.save_all(dtos)
