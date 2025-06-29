import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("application > services > company_service")
from application.usecases.sync_companies import SyncCompaniesUseCase
# from domain.dto import SyncCompaniesResultDTO
from domain.ports import CompanyRepositoryPort, CompanySourcePort
from infrastructure.config import Config
from infrastructure.logging import Logger


class CompanyService:
    """
    Application Service que coordena os casos de uso relacionados a Company.
    """
    import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("class company_service")

    def __init__(
        self,
        config: Config,
        logger: Logger,
        repository: CompanyRepositoryPort,
        scraper: CompanySourcePort,
    ):
        """Initialize the service with injected repository and scraper."""
        import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("class company_service __init__")
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
#         """
#         Executa a sincronização de empresas usando o caso de uso apropriado.
#         """
#         return self.sync_usecase.execute()
    def run(self) -> None:
        """
        Executa a sincronização de empresas usando o caso de uso apropriado.
        """
        import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("class company_service run")
        self.sync_usecase.execute()
