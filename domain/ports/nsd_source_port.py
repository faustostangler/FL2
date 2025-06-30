"""Port definitions for external NSD data providers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable, Dict, List, Optional, Set

from .metrics_collector_port import MetricsCollectorPort


class NSDSourcePort(ABC):
    """Port for external NSD data providers."""

    @abstractmethod
    def fetch_all(
        self,
        start: int = 1,
        max_nsd: Optional[int] = None,
        skip_codes: Optional[Set[int]] = None,
        save_callback: Optional[Callable[[List[Dict]], None]] = None,
        threshold: Optional[int] = None,
    ) -> List[Dict]:
        """Fetch all available NSD records."""
        raise NotImplementedError

    @property
    @abstractmethod
    def metrics_collector(self) -> MetricsCollectorPort:
        """Metrics collector used by the scraper."""
        raise NotImplementedError
