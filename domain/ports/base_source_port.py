"""Generic interface for external data sources."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable, Generic, List, Optional, Set, TypeVar

from domain.dto import ExecutionResultDTO

T = TypeVar("T")


class BaseSourcePort(ABC, Generic[T]):
    """Generic port for external data providers."""

    @abstractmethod
    def fetch_all(
        self,
        threshold: Optional[int] = None,
        skip_codes: Optional[Set[str]] = None,
        save_callback: Optional[Callable[[List[T]], None]] = None,
        max_workers: Optional[int] = None,
    ) -> ExecutionResultDTO[T]:
        """Retrieve all available records."""
        raise NotImplementedError
