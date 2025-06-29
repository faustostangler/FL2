from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Set

from domain.dto.nsd_dto import NSDDTO


class NSDRepositoryPort(ABC):
    """Port for NSD persistence operations."""

    @abstractmethod
    def save_all(self, items: List[NSDDTO]) -> None:
        """Persist a batch of NSD records."""
        raise NotImplementedError

    @abstractmethod
    def get_all_primary_keys(self) -> Set[int]:
        """Return all stored NSD identifiers."""
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, id: int) -> NSDDTO:
        """Retrieve an NSD record by its ID."""
        raise NotImplementedError
