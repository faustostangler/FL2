from __future__ import annotations

from infrastructure.logging import Logger
from infrastructure.repositories.nsd_repository import SQLiteNSDRepository
from infrastructure.scrapers.nsd_scraper import NsdScraper
from application.usecases.sync_nsd import SyncNSDUseCase


class NsdService:
    """Application service that orchestrates NSD scraping and persistence."""

    def __init__(
        self, logger: Logger, repository: SQLiteNSDRepository, scraper: NsdScraper
    ) -> None:
        self.logger = logger
        logger.log("Start NsdService", level="info")

        self.sync_usecase = SyncNSDUseCase(
            logger=self.logger, repository=repository, scraper=scraper
        )

    def run(self) -> None:
        """Run the NSD synchronization workflow."""
        self.sync_usecase.execute()
