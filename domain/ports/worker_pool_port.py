from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Generic, Iterable, List, Optional, Protocol, TypeVar

T = TypeVar("T")
R = TypeVar("R")


class LoggerPort(Protocol):
    def log(
        self,
        message: str,
        level: str = "info",
        progress: Optional[dict] = None,
        extra: Optional[dict] = None,
        worker_id: Optional[str] = None,
    ) -> None:
        raise NotImplemented


@dataclass
class Metrics:
    elapsed_time: float
    network_bytes: int = 0
    processing_bytes: int = 0
    failures: int = 0

    @property
    def total_bytes(self) -> int:
        return self.network_bytes + self.processing_bytes

    # Backwards compatibility
    @property
    def download_bytes(self) -> int:  # noqa: D401
        """Alias for ``total_bytes`` for legacy callers."""
        return self.total_bytes


@dataclass
class ExecutionResult(Generic[R]):
    """Return value of ``WorkerPoolPort.run``."""

    items: List[R]
    metrics: Metrics


class WorkerPoolPort(Protocol):
    def run(
        self,
        tasks: Iterable[T],
        processor: Callable[[T], R],
        logger: LoggerPort,
        on_result: Optional[Callable[[R], None]] = None,
        post_callback: Optional[Callable[[List[R]], None]] = None,
    ) -> ExecutionResult[R]:
        raise NotImplemented
