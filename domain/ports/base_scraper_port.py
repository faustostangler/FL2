"""Generic interface for external data sources."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable, Generic, List, Optional, Set, TypeVar

from domain.dto import ExecutionResultDTO

from .metrics_collector_port import MetricsCollectorPort

T = TypeVar("T")


class BaseScraperPort(ABC, Generic[T]):
    """Generic port for external data providers."""

    @abstractmethod
    def fetch_all(
        self,
        threshold: Optional[int] = None,
        skip_codes: Optional[Set[str]] = None,
        save_callback: Optional[Callable[[List[T]], None]] = None,
        **kwargs,
    ) -> ExecutionResultDTO[T]:
        """Retrieve all available records."""
        raise NotImplementedError

    @property
    @abstractmethod
    def metrics_collector(self) -> MetricsCollectorPort:
        """Metrics collector used by the scraper."""
        raise NotImplementedError
