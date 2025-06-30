"""Core execution port definitions for the worker pool interface."""

from __future__ import annotations

from typing import Callable, Iterable, List, Optional, Protocol, TypeVar

from domain.dto import ExecutionResultDTO

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
