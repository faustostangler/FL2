from typing import List

import utils.logging as logging_utils
from domain.models.company_dto import CompanyDTO
from infrastructure.repositories.base_repository import BaseRepository
from infrastructure.scrapers.company_scraper import CompanyScraper

class SyncCompaniesUseCase:
    """
    UseCase responsável por sincronizar os dados das empresas da fonte externa com o repositório local.
    """

    def __init__(self, repository: BaseRepository[CompanyDTO], scraper: CompanyScraper):
        logging_utils.log_message("Start SyncCompaniesUseCase", level="info")

        self.repository = repository
        self.scraper = scraper

    def execute(self) -> None:
        """
        Executa a sincronização:
        - Carrega dados do scraper (fonte externa)
        - Converte para CompanyDTO
        - Persiste no repositório
        """
        raw_data: List[dict] = self.scraper.fetch_all()
        dtos: List[CompanyDTO] = [CompanyDTO.from_dict(row) for row in raw_data]
        self.repository.save_all(dtos)
