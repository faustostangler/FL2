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
        self.logger = logger
        self.logger.log("Start NsdService", level="info")

        self.sync_usecase = SyncNSDUseCase(
            logger=self.logger, repository=repository, scraper=scraper
        )

    def run(self) -> None:
        """Run the NSD synchronization workflow."""
        self.sync_usecase.execute()
