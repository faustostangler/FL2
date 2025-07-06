from application.usecases.sync_companies import SyncCompaniesUseCase
from domain.ports import CompanyRepositoryPort, CompanySourcePort, LoggerPort
from infrastructure.config import Config


class CompanyService:
    """Coordinate company-related use cases within the application."""

    def __init__(
        self,
        config: Config,
        logger: LoggerPort,
        repository: CompanyRepositoryPort,
        scraper: CompanySourcePort,
    ):
        """Initialize dependencies for company synchronization."""
        self.logger = logger
        self.config = config

        # Create the use case responsible for performing the sync operation.
        self.sync_companies_usecase = SyncCompaniesUseCase(
            logger=self.logger,
            repository=repository,
            scraper=scraper,
            max_workers=self.config.global_settings.max_workers,
        )

        self.logger.log(f"Start Class {self.__class__.__name__}", level="info")

    def run(self):
        """Execute company synchronization using the injected use case."""
        # Delegate execution to the underlying use case and return the result.
        self.logger.log("Start Sync Companies Use Case in CompanyService", level="info")
        result = self.sync_companies_usecase.run()
        self.logger.log("End Sync Companies Use Case in CompanyService", level="info")
        return result
