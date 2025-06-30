"""Core execution port definitions for the worker pool interface."""

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
        """Emit a log message from a worker thread."""

        raise NotImplementedError


@dataclass(frozen=True)
class MetricsDTO:
    elapsed_time: float
    network_bytes: int = 0
    processing_bytes: int = 0
    failures: int = 0


@dataclass(frozen=True)
class ExecutionResultDTO(Generic[R]):
    """Results and metrics returned by :class:`WorkerPoolPort.run`."""

    items: List[R]
    metrics: MetricsDTO


class WorkerPoolPort(Protocol):
    def run(
        self,
        tasks: Iterable[T],
        processor: Callable[[T], R],
        logger: LoggerPort,
        on_result: Optional[Callable[[R], None]] = None,
        post_callback: Optional[Callable[[List[R]], None]] = None,
    ) -> ExecutionResultDTO[R]:
        """Execute tasks concurrently using worker threads."""

        raise NotImplementedError
