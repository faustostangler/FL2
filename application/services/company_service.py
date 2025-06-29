import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("application > services > company_service")
from application.usecases.sync_companies import SyncCompaniesUseCase
# from domain.dto import SyncCompaniesResultDTO
from domain.ports import CompanyRepositoryPort, CompanySourcePort
from infrastructure.config import Config
from infrastructure.logging import Logger


class CompanyService:
    """Coordinate company-related use cases within the application."""
    import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("company_service.CompanyService")

    def __init__(
        self,
        config: Config,
        logger: Logger,
        repository: CompanyRepositoryPort,
        scraper: CompanySourcePort,
    ):
        """Initialize dependencies for company synchronization."""
        import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("company_service.CompanyService.__init__")
        self.logger = logger
        self.config = config
        logger.log("Start CompanyService", level="info")

        self.sync_usecase = SyncCompaniesUseCase(
            logger=self.logger,
            repository=repository,
            scraper=scraper,
            max_workers=self.config.global_settings.max_workers,
        )

#     def run(self) -> SyncCompaniesResultDTO:
#         """Run company synchronization and return a result summary."""
#         return self.sync_usecase.execute()
    def run(self) -> None:
        """Execute company synchronization using the injected use case."""
        import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("company_service.CompanyService.run()")
        self.sync_usecase.execute()
