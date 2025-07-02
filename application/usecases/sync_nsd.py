from __future__ import annotations

from domain.dto.nsd_dto import NsdDTO
from domain.ports import LoggerPort, NSDRepositoryPort, NSDSourcePort


class SyncNSDUseCase:
    """Use case responsible for synchronizing NSD documents."""

    def __init__(
        self,
        logger: LoggerPort,
        repository: NSDRepositoryPort,
        scraper: NSDSourcePort,
    ) -> None:
        """Store dependencies required for synchronization."""
        self.logger = logger
        # Log that the use case has started for easier debugging.
        self.logger.log("Start SyncNSDUseCase", level="info")

        # Repositories and scrapers provide the IO boundary for NSD documents.
        self.repository = repository
        self.scraper = scraper

    def run(self) -> None:
        """Run the NSD synchronization workflow."""
        # Retrieve any previously stored document IDs to avoid duplicates.
        existing_ids = self.repository.get_all_primary_keys()

        # Fetch all documents from the scraper, persisting them in batches.
        self.scraper.fetch_all(
            skip_codes=existing_ids,
            save_callback=self._save_batch,
        )

        # Record metrics about the synchronization process.
        self.logger.log(
            f"Downloaded {self.scraper.metrics_collector.network_bytes} bytes",
            level="info",
        )

    def _save_batch(self, buffer: list[NsdDTO]) -> None:
        """Persist a batch of raw data after converting to domain DTOs."""
        # Save the batch to the repository in a single call.
        self.repository.save_all(buffer)
