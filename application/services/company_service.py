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
        self.logger.log("Start CompanyService", level="info")

        self.sync_usecase = SyncCompaniesUseCase(
            logger=self.logger,
            repository=repository,
            scraper=scraper,
            max_workers=self.config.global_settings.max_workers,
        )

    def run(self):
        """Execute company synchronization using the injected use case."""
        return self.sync_usecase.execute()
