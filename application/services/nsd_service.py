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
        # Log the start of the service for observability.
        self.logger.log("Start NsdService", level="info")

        # Set up the underlying use case that performs the synchronization.
        self.sync_nsd_usecase = SyncNSDUseCase(
            logger=self.logger, repository=repository, scraper=scraper
        )

    def run(self) -> None:
        """Run the NSD synchronization workflow."""
        # Delegate the work to the injected use case.
        self.sync_nsd_usecase.run()
        self.logger.log("Finish NsdService", level="info")
