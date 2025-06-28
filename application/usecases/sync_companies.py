import time
from typing import List

from domain.dto import SyncCompaniesResultDTO
from domain.dto.company_dto import CompanyDTO
from domain.dto.raw_company_dto import CompanyRawDTO
from domain.ports import CompanyRepositoryPort, CompanySourcePort
from infrastructure.logging import Logger


class SyncCompaniesUseCase:
    """
    UseCase responsável por sincronizar os dados das empresas da fonte externa com o repositório local.
    """

    def __init__(
        self,
        logger: Logger,
        repository: CompanyRepositoryPort,
        scraper: CompanySourcePort,
        max_workers: int,
    ):
        self.logger = logger
        self.logger.log("Start SyncCompaniesUseCase", level="info")

        self.repository = repository
        self.scraper = scraper
        self.max_workers = max_workers

    def execute(self) -> SyncCompaniesResultDTO:
        """
        Executa a sincronização:
        - Carrega dados do scraper (fonte externa)
        - Converte para CompanyDTO
        - Persiste no repositório
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

        return SyncCompaniesResultDTO(
            processed_count=len(results),
            skipped_count=len(existing_codes),
            bytes_downloaded=bytes_downloaded,
            elapsed_time=elapsed,
        )

    def _save_batch(self, buffer: List[CompanyRawDTO]) -> None:
        """Convert raw companies to domain DTOs before saving."""

        dtos = [CompanyDTO.from_raw(item) for item in buffer]
        self.repository.save_all(dtos)
