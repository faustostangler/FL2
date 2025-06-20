from infrastructure.logging import Logger
from infrastructure.repositories import SQLiteCompanyRepository
from infrastructure.scrapers.company_b3_scraper import CompanyB3Scraper

from application.usecases.sync_companies import SyncCompaniesUseCase

class CompanyService:
    """
    Application Service que coordena os casos de uso relacionados a Company.
    """

    def __init__(self, logger: Logger, repository: SQLiteCompanyRepository, scraper: CompanyB3Scraper):
        """
        Initializes the CompanyService with the provided repository and scraper.
        Args:
            repository (SQLiteCompanyRepository): The repository instance for company data persistence.
            scraper (CompanyB3Scraper): The scraper instance for fetching company data from B3.
        """
        self.logger = logger
        logger.log("Start CompanyService", level="info")

        self.sync_usecase = SyncCompaniesUseCase(repository, scraper)

    def run(self) -> None:
        """
        Executa a sincronização de empresas usando o caso de uso apropriado.
        """
        self.sync_usecase.execute()
