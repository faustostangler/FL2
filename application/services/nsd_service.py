from __future__ import annotations

from infrastructure.logging import Logger
# from infrastructure.repositories.nsd_repository import SQLiteNSDRepository
# from infrastructure.scrapers.nsd_scraper import NsdScraper


class NsdService:
    """Application service that orchestrates NSD scraping and persistence."""

    def __init__(
        self, logger: Logger, repository: SQLiteNSDRepository, scraper: NsdScraper
    ):
        self.logger = logger
        logger.log("Start NsdService", level="info")

        self.repository = repository
        self.scraper = scraper

    def run(self) -> None:
        """Run the NSD synchronization workflow."""
        data = self.scraper.fetch_all()
        self.repository.save_all(data)
