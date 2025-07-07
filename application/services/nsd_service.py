from __future__ import annotations

from application.usecases.sync_nsd import SyncNSDUseCase
from domain.ports import LoggerPort, NSDRepositoryPort, NSDSourcePort


class NsdService:
    """Application service that orchestrates NSD synchronization."""

    def __init__(
        self,
        logger: LoggerPort,
        repository: NSDRepositoryPort,
        scraper: NSDSourcePort,
    ) -> None:
        """Instantiate the service with its required dependencies."""
        self.logger = logger

        # Set up the underlying use case that performs the synchronization.
        self.sync_nsd_usecase = SyncNSDUseCase(
            logger=self.logger, repository=repository, scraper=scraper
        )

        # self.logger.log(f"Load Class {self.__class__.__name__}", level="info")

    def run(self) -> None:
        """Start the NSD synchronization workflow."""
        # Delegate the work to the injected use case.
        # self.logger.log("Call Method controller.run()._nsd_service().run().sync_nsd_usecase.run()", level="info")
        self.sync_nsd_usecase.run()
        # self.logger.log("End  Method controller.run()._nsd_service().run().sync_nsd_usecase.run()", level="info")
