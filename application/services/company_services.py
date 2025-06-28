from infrastructure.config import Config
from infrastructure.logging import Logger
from domain.ports import CompanyRepositoryPort, CompanySourcePort

from application.usecases.sync_companies import SyncCompaniesUseCase


class CompanyService:
    """
    Application Service que coordena os casos de uso relacionados a Company.
    """

    def __init__(
        self,
        config: Config,
        logger: Logger,
        repository: CompanyRepositoryPort,
        scraper: CompanySourcePort,
    ):
        """Initialize the service with injected repository and scraper."""
        self.logger = logger
        self.config = config
        logger.log("Start CompanyService", level="info")

        self.sync_usecase = SyncCompaniesUseCase(
            config=self.config,
            logger=self.logger,
            repository=repository,
            scraper=scraper,
        )

    def run(self) -> None:
        """
        Executa a sincronização de empresas usando o caso de uso apropriado.
        """
        self.sync_usecase.execute()
