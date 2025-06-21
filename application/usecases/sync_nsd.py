from __future__ import annotations

from typing import Set

from infrastructure.logging import Logger
from infrastructure.repositories.nsd_repository import SQLiteNSDRepository
from infrastructure.scrapers.nsd_scraper import NsdScraper
from domain.dto.nsd_dto import NSDDTO


class SyncNSDUseCase:
    """Synchronize NSD records from external source with the repository."""

    def __init__(
        self, logger: Logger, repository: SQLiteNSDRepository, scraper: NsdScraper
    ) -> None:
        self.logger = logger
        self.logger.log("Start SyncNSDUseCase", level="info")

        self.repository = repository
        self.scraper = scraper

    def execute(self) -> None:
        """Fetch new NSDs and persist them if not already stored."""
        existing_ids = self._load_existing_ids()
        self.logger.log(f"Loaded {len(existing_ids)} existing NSDs", level="info")

        try:
            raw_items = self.scraper.fetch_all(skip_nsd=existing_ids)
        except TypeError:
            raw_items = self.scraper.fetch_all()

        new_entries = [
            item for item in raw_items if item.get("nsd") not in existing_ids
        ]
        self.logger.log(f"Fetched {len(new_entries)} new NSD records", level="info")

        dtos = [NSDDTO.from_dict(item) for item in new_entries]
        if dtos:
            self.repository.save_all(dtos)
            self.logger.log(f"Saved {len(dtos)} NSDs", level="info")

    def _load_existing_ids(self) -> Set[int]:
        """Return a set of NSD identifiers already stored."""
        if hasattr(self.repository, "list_existing_ids"):
            ids = self.repository.list_existing_ids()
            return {int(i) for i in ids}

        all_items = self.repository.get_all()
        return {int(dto.nsd) for dto in all_items}
