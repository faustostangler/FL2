from __future__ import annotations

from abc import ABC, abstractmethod


class StatementSourcePort(ABC):
    """Port for fetching raw statement HTML."""

    @abstractmethod
    def fetch(self, batch_id: str) -> str:
        """Return raw HTML for the given batch identifier."""
        raise NotImplementedError

    @property
    @abstractmethod
    def endpoint(self) -> str:
        """Base endpoint used by the adapter (for inspection/testing)."""
        raise NotImplementedError
