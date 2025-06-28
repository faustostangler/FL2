from typing import List

from domain.dto.company_dto import CompanyDTO
from domain.dto.raw_company_dto import CompanyRawDTO
from infrastructure.config import Config
from infrastructure.logging import Logger
from infrastructure.repositories import SQLiteCompanyRepository
from infrastructure.scrapers.company_b3_scraper import CompanyB3Scraper


class SyncCompaniesUseCase:
    """
    UseCase responsável por sincronizar os dados das empresas da fonte externa com o repositório local.
    """

    def __init__(
        self,
        config: Config,
        logger: Logger,
        repository: SQLiteCompanyRepository,
        scraper: CompanyB3Scraper,
    ):
        self.config = config
        self.logger = logger
        self.logger.log("Start SyncCompaniesUseCase", level="info")

        self.repository = repository
        self.scraper = scraper

    def execute(self) -> None:
        """
        Executa a sincronização:
        - Carrega dados do scraper (fonte externa)
        - Converte para CompanyDTO
        - Persiste no repositório
        """
        self.logger.log("SyncCompaniesUseCase Execute", level="info")

        existing_codes = self.repository.get_all_primary_keys()

        self.scraper.fetch_all(
            skip_codes=existing_codes,
            save_callback=self._save_batch,
            max_workers=self.config.global_settings.max_workers,
        )
        self.logger.log(
            f"Downloaded {self.scraper.metrics_collector.network_bytes} bytes",
            level="info",
        )

    def _save_batch(self, buffer: List[CompanyRawDTO]) -> None:
        """Converte dados brutos em ``CompanyDTO`` e salva no repositório."""

        dtos = [CompanyDTO.from_raw(item) for item in buffer]
        self.repository.save_all(dtos)
