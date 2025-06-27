from typing import List

from infrastructure.config import Config

from infrastructure.logging import Logger
from infrastructure.repositories import SQLiteCompanyRepository
from infrastructure.scrapers.company_b3_scraper import CompanyB3Scraper
from application import CompanyMapper


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
        mapper: CompanyMapper,
    ):
        self.config = config
        self.logger = logger
        self.logger.log("Start SyncCompaniesUseCase", level="info")

        self.repository = repository
        self.scraper = scraper
        self.mapper = mapper

    def execute(self) -> None:
        """
        Executa a sincronização:
        - Carrega dados do scraper (fonte externa)
        - Converte para RawCompanyDTO
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
            f"Downloaded {self.scraper.total_bytes_downloaded} bytes",
            level="info",
        )

    def _save_batch(self, buffer: List[dict]) -> None:
        dtos = [self.mapper.from_raw_dicts(item["base"], item["detail"]) for item in buffer]
        self.repository.save_all(dtos)
