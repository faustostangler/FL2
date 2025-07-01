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
        # Log startup so we know when the service begins.
        self.logger.log("Start CompanyService", level="info")

        # Create the use case responsible for performing the sync operation.
        self.sync_usecase = SyncCompaniesUseCase(
            logger=self.logger,
            repository=repository,
            scraper=scraper,
            max_workers=self.config.global_settings.max_workers,
        )

    def run(self):
        """Execute company synchronization using the injected use case."""
        # Delegate execution to the underlying use case and return the result.
        return self.sync_usecase.run()
