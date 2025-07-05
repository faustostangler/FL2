from __future__ import annotations

from abc import ABC, abstractmethod

from domain.dto.nsd_dto import NsdDTO


class StatementSourcePort(ABC):
    """Port for fetching raw statement HTML."""

    @abstractmethod
    def fetch(self, row: NsdDTO) -> str:
        """Return raw HTML for the given batch identifier."""
        raise NotImplementedError
