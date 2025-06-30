"""Port definitions for company persistence repositories."""

from __future__ import annotations

from abc import abstractmethod
from typing import Set

from domain.dto.company_dto import CompanyDTO

from .base_repository_port import BaseRepositoryPort


class CompanyRepositoryPort(BaseRepositoryPort[CompanyDTO]):
    """Port for company persistence operations."""

    @abstractmethod
    def get_all_primary_keys(self) -> Set[str]:
        """Return all stored CVM codes."""
        raise NotImplementedError
