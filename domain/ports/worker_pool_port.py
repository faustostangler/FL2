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
        raise NotImplementedError


@dataclass
class Metrics:

    elapsed_time: float
    network_bytes: int = 0
    processing_bytes: int = 0
    failures: int = 0


@dataclass
class ExecutionResult(Generic[R]):
    """Results and metrics returned by :class:`WorkerPoolPort.run`."""

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
        raise NotImplementedError
