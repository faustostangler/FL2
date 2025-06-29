import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("domain > ports > worker_pool_port")
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Generic, Iterable, List, Optional, Protocol, TypeVar

T = TypeVar("T")
R = TypeVar("R")


class LoggerPort(Protocol):
    import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("worker_pool_port class LoggerPort")

    def log(
        self,
        message: str,
        level: str = "info",
        progress: Optional[dict] = None,
        extra: Optional[dict] = None,
        worker_id: Optional[str] = None,
    ) -> None:
        import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("LoggerPort.log()")
        raise NotImplementedError


@dataclass
class Metrics:
    import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("worker_pool_port class Metrics")

    elapsed_time: float
    network_bytes: int = 0
    processing_bytes: int = 0
    failures: int = 0


@dataclass
class ExecutionResult(Generic[R]):
    """Results and metrics returned by :class:`WorkerPoolPort.run`."""
    import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("worker_pool_port class ExecutionResult(Generic[R])")

    items: List[R]
    metrics: Metrics


class WorkerPoolPort(Protocol):
    import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("worker_pool_port class WoWorkerPoolPort(Protocol)")

    def run(
        self,
        tasks: Iterable[T],
        processor: Callable[[T], R],
        logger: LoggerPort,
        on_result: Optional[Callable[[R], None]] = None,
        post_callback: Optional[Callable[[List[R]], None]] = None,
    ) -> ExecutionResult[R]:
        import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("WoWorkerPoolPort(Protocol).run()")
        raise NotImplementedError
