"""Port definitions for external NSD data providers."""

from __future__ import annotations

from typing import Callable, List, Optional, Set, TypeVar

from domain.dto import ExecutionResultDTO, NsdDTO

from .base_source_port import BaseSourcePort

T = TypeVar("T")


class NSDSourcePort(BaseSourcePort[NsdDTO]):
    """Port for external NSD data providers."""
    def fetch_all(
        self,
        threshold: Optional[int] = None,
        skip_codes: Optional[Set[str]] = None,
        save_callback: Optional[Callable[[List[NsdDTO]], None]] = None,
        max_workers: Optional[int] = None,
        start: int = 1,
        max_nsd: Optional[int] = None,
        **kwargs,
    ) -> ExecutionResultDTO[NsdDTO]:
        raise NotImplementedError
