from __future__ import annotations

import json
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
from typing import Any, Callable, Iterable, List, Optional, Tuple, TypeVar

from domain.dto import ExecutionResultDTO, WorkerTaskDTO
from domain.ports import MetricsCollectorPort
from domain.ports.worker_pool_port import (
    LoggerPort,
    WorkerPoolPort,
)
from infrastructure.config import Config
from infrastructure.helpers.byte_formatter import ByteFormatter

T = TypeVar("T")
R = TypeVar("R")


class WorkerPool(WorkerPoolPort):
    """Simple thread pool implementation tied to the domain
    ``WorkerPoolPort``."""

    def __init__(
        self,
        config: Config,
        metrics_collector: MetricsCollectorPort,
        max_workers: Optional[int] = None,
    ) -> None:
        """Initialize the worker pool with configuration and metrics."""

        self.config = config
        self.metrics_collector = metrics_collector
        self.max_workers = max_workers or config.global_settings.max_workers or 1
        self.byte_formatter = ByteFormatter()

    def run(
        self,
        tasks: Iterable[Tuple[int, Any]],
        processor: Callable[[T], R],
        logger: LoggerPort,
        on_result: Optional[Callable[[R], None]] = None,
        post_callback: Optional[Callable[[List[R]], None]] = None,
    ) -> ExecutionResultDTO[R]:
        """Process ``tasks`` concurrently using ``processor``."""

        # Inform about the worker pool startup
        logger.log("Worker pool start", level="info")

        results: List[R] = []
        queue: Queue = Queue(self.config.global_settings.queue_size)
        lock = threading.Lock()
        sentinel = object()
        start_time = time.perf_counter()

        def worker(worker_id: str) -> None:
            logger.log(f"worker {worker_id} started", level="info", worker_id=worker_id)
            while True:
                item = queue.get()
                index, entry = item
                task = WorkerTaskDTO(index=index, data=entry, worker_id=worker_id)
                logger.log(f"worker {worker_id} got another task from qeue {queue.unfinished_tasks} tasks", level="info", worker_id=worker_id)
                if item is sentinel:
                    queue.task_done()
                    break
                try:
                    logger.log(f"running {item[1]['codeCVM']}", level="info")
                    result = processor(task)

                    self.metrics_collector.record_processing_bytes(
                        len(json.dumps(result, default=str).encode("utf-8"))
                    )
                    with lock:
                        results.append(result)
                        if callable(on_result):
                            on_result(result)
                except Exception as exc:  # noqa: BLE001
                    logger.log(
                        f"worker error: {exc}", level="warning", worker_id=worker_id
                    )
                finally:
                    queue.task_done()

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            logger.log(f"ThreadPoolExecutor started with {self.max_workers} workers", level="info")
            futures = [
                executor.submit(worker, uuid.uuid4().hex[:8])
                for _ in range(self.max_workers)
            ]

            for task in tasks:
                queue.put(task)

            for _ in range(self.max_workers):
                queue.put(sentinel)

            queue.join()

            logger.log("ThreadPoolExecutor finished", level="info")

            for future in futures:
                future.result()

        elapsed = time.perf_counter() - start_time

        # Package execution metrics (network and processing bytes)
        metrics = self.metrics_collector.get_metrics(elapsed_time=elapsed)

        # Final callback after all tasks are done
        if callable(post_callback):
            logger.log("Callable found", level="info")
            post_callback(results)

        # Summarize execution in the logs
        logger.log(
            f"Executed {len(results)} tasks in {elapsed:.2f}s ("
            f"{self.byte_formatter.format_bytes(self.metrics_collector.processing_bytes)} {self.byte_formatter.format_bytes(self.metrics_collector.network_bytes)})",
            level="info",
        )

        return ExecutionResultDTO(items=results, metrics=metrics)
