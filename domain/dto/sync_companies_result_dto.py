import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("domain > dto > sync_companies_dto")
from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class SyncCompaniesResultDTO:
    """Summary information returned by :class:`SyncCompaniesUseCase`."""
    import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("sync_companies_dto class SyncCompaniesResultDTO")

    processed_count: int
    skipped_count: int
    bytes_downloaded: int
    elapsed_time: float
    warnings: Optional[List[str]] = None
