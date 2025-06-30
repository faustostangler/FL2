"""Port definitions for NSD persistence repositories."""

from __future__ import annotations

from abc import abstractmethod
from typing import Set

from domain.dto.nsd_dto import NSDDTO

from .base_repository_port import BaseRepositoryPort


class NSDRepositoryPort(BaseRepositoryPort[NSDDTO]):
    """Port for NSD persistence operations."""

    @abstractmethod
    def get_all_primary_keys(self) -> Set[int]:
        """Return all stored NSD identifiers."""
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, id: int) -> NSDDTO:
        """Retrieve an NSD record by its ID."""
        raise NotImplementedError
