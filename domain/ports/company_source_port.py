from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable, List, Optional, Set

from domain.dto.raw_company_dto import CompanyRawDTO


class CompanySourcePort(ABC):
    """Port for external company data providers."""

    @abstractmethod
    def fetch_all(
        self,
        threshold: Optional[int] = None,
        skip_codes: Optional[Set[str]] = None,
        save_callback: Optional[Callable[[List[CompanyRawDTO]], None]] = None,
        max_workers: int | None = None,
    ) -> List[CompanyRawDTO]:
        """Fetch all available companies."""
        raise NotImplementedError
