from infrastructure.config import Config
from infrastructure.logging import Logger
from infrastructure.repositories import SQLiteCompanyRepository
from infrastructure.scrapers.company_b3_scraper import CompanyB3Scraper

from application.usecases.sync_companies import SyncCompaniesUseCase
from application.usecases.threaded_sync_companies import (
    MultiThreadedSyncCompaniesUseCase,
)


class CompanyService:
    """
    Application Service que coordena os casos de uso relacionados a Company.
    """

    def __init__(
        self,
        config: Config,
        logger: Logger,
        repository: SQLiteCompanyRepository,
        scraper: CompanyB3Scraper,
    ):
        """
        Initializes the CompanyService with the provided repository and scraper.
        Args:
            repository (SQLiteCompanyRepository): The repository instance for company data persistence.
            scraper (CompanyB3Scraper): The scraper instance for fetching company data from B3.
        """
        self.logger = logger
        self.config = config
        logger.log("Start CompanyService", level="info")

        if (self.config.global_settings.max_workers or 1) > 1:
            self.sync_usecase = MultiThreadedSyncCompaniesUseCase(
                config=self.config,
                logger=self.logger,
                repository=repository,
                scraper=scraper,
            )
        else:
            self.sync_usecase = SyncCompaniesUseCase(
                logger=self.logger,
                repository=repository,
                scraper=scraper,
            )

    def run(self) -> None:
        """
        Executa a sincronização de empresas usando o caso de uso apropriado.
        """
        self.sync_usecase.execute()
