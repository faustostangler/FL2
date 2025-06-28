from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Set

from domain.dto.company_dto import CompanyDTO


class CompanyRepositoryPort(ABC):
    """Port for company persistence operations."""

    @abstractmethod
    def save_all(self, items: List[CompanyDTO]) -> None:
        """Persist a batch of companies."""
        raise NotImplementedError

    @abstractmethod
    def get_all_primary_keys(self) -> Set[str]:
        """Return all stored CVM codes."""
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, id: str) -> CompanyDTO:
        """Retrieve a company by its CVM code."""
        raise NotImplementedError
