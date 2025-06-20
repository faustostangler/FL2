from typing import List

import utils.logging as logging_utils
from infrastructure.config import Config
from domain.dto.company_dto import CompanyDTO
from infrastructure.repositories import SQLiteCompanyRepository
from infrastructure.scrapers.company_b3_scraper import CompanyB3Scraper

config = Config()

class SyncCompaniesUseCase:
    """
    UseCase responsável por sincronizar os dados das empresas da fonte externa com o repositório local.
    """

    def __init__(self, repository: SQLiteCompanyRepository, scraper: CompanyB3Scraper):
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
        existing_codes = self.repository.get_all_cvm_codes()
        self.scraper.fetch_all(skip_cvm_codes=existing_codes, save_callback=self._save_batch)

    def _save_batch(self, buffer: List[dict]) -> None:
        dtos = [CompanyDTO.from_dict(d) for d in buffer]
        self.repository.save_all(dtos)
