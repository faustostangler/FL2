from application.usecases.sync_companies import SyncCompaniesUseCase
from infrastructure.repositories.company_repository import SQLiteCompanyRepository
from infrastructure.scrapers.company_b3_scraper import CompanyB3Scraper

import utils.logging as logging_utils
class CompanyService:
    """
    Application Service que coordena os casos de uso relacionados a Company.
    """

    def __init__(self, repository: SQLiteCompanyRepository, scraper: CompanyB3Scraper):
        """
        Initializes the CompanyService with the provided repository and scraper.
        Args:
            repository (SQLiteCompanyRepository): The repository instance for company data persistence.
            scraper (CompanyB3Scraper): The scraper instance for fetching company data from B3.
        """
        logging_utils.log_message("Start CompanyService", level="info")

        self.sync_usecase = SyncCompaniesUseCase(repository, scraper)

    def run(self) -> None:
        """
        Executa a sincronização de empresas usando o caso de uso apropriado.
        """
        self.sync_usecase.execute()
