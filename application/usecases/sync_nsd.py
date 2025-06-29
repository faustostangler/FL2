from __future__ import annotations

from domain.dto.nsd_dto import NSDDTO
from domain.ports import LoggerPort, NSDRepositoryPort, NSDSourcePort


class SyncNSDUseCase:
    """Use case responsible for synchronizing NSD documents."""

    def __init__(
        self,
        logger: LoggerPort,
        repository: NSDRepositoryPort,
        scraper: NSDSourcePort,
    ) -> None:
        self.logger = logger
        self.logger.log("Start SyncNSDUseCase", level="info")

        self.repository = repository
        self.scraper = scraper

    def execute(self) -> None:
        """Run the NSD synchronization workflow."""
        existing_ids = self.repository.get_all_primary_keys()
        self.scraper.fetch_all(
            skip_codes=existing_ids,
            save_callback=self._save_batch,
        )
        self.logger.log(
            f"Downloaded {self.scraper.metrics_collector.network_bytes} bytes",
            level="info",
        )

    def _save_batch(self, buffer: list[dict]) -> None:
        dtos = [NSDDTO.from_dict(d) for d in buffer]
        self.repository.save_all(dtos)
