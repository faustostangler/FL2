from __future__ import annotations


from infrastructure.logging import Logger
from domain.dto.nsd_dto import NSDDTO
from infrastructure.repositories.nsd_repository import SQLiteNSDRepository
from infrastructure.scrapers.nsd_scraper import NsdScraper


class SyncNSDUseCase:
    """Use case responsible for synchronizing NSD documents."""

    def __init__(
        self, logger: Logger, repository: SQLiteNSDRepository, scraper: NsdScraper
    ):
        self.logger = logger
        self.logger.log("Start SyncNSDUseCase", level="info")

        self.repository = repository
        self.scraper = scraper

    def execute(self) -> None:
        """Run the NSD synchronization workflow."""
        raw_list = self.scraper.fetch_all()
        dtos = [NSDDTO.from_dict(item) for item in raw_list]
        self.repository.save_all(dtos)
