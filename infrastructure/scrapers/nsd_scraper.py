from __future__ import annotations

from typing import List

from infrastructure.config import Config
from infrastructure.logging import Logger


class NsdScraper:
    """Simple scraper placeholder for NSD documents."""

    def __init__(self, config: Config, logger: Logger):
        self.config = config
        self.logger = logger
        self.logger.log("Start NsdScraper", level="info")

    def fetch_all(self) -> List[dict]:
        """Return raw NSD data (placeholder implementation)."""
        self.logger.log("Fetch NSD list", level="info")
        return []
