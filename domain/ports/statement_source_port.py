from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from domain.dto.nsd_dto import NsdDTO


class StatementSourcePort(ABC):
    """Port for fetching raw statement HTML."""

    @abstractmethod
    def fetch(self, row: NsdDTO) -> dict[str, Any]:
        """Return statement rows for the given NSD."""
        raise NotImplementedError
