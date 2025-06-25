from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, List, Optional, Protocol, Tuple, TypeVar

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
    ) -> None: ...


@dataclass
class Metrics:
    elapsed_time: float
    download_bytes: int
    failures: int = 0


class WorkerPoolPort(Protocol):
    def run(
        self,
        tasks: Iterable[T],
        processor: Callable[[T], R],
        logger: LoggerPort,
        post_callback: Optional[Callable[[List[R]], None]] = None,
    ) -> Tuple[List[R], Metrics]: ...
