from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class SyncCompaniesResultDTO:
    """Summary information returned by :class:`SyncCompaniesUseCase`."""

    processed_count: int
    skipped_count: int
    bytes_downloaded: int
    elapsed_time: float
    warnings: Optional[List[str]] = None
