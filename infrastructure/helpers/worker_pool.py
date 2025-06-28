from __future__ import annotations

import json
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
from typing import Callable, Iterable, List, Optional, TypeVar

from domain.ports.worker_pool_port import (
    ExecutionResult,
    LoggerPort,
    WorkerPoolPort,
)
from infrastructure.config import Config
from infrastructure.helpers.byte_formatter import ByteFormatter
from infrastructure.helpers.metrics_collector import MetricsCollector

T = TypeVar("T")
R = TypeVar("R")


class WorkerPool(WorkerPoolPort):
    def __init__(
        self,
        config: Config,
        metrics_collector: MetricsCollector,
        max_workers: Optional[int] = None,
    ) -> None:
        self.config = config
        self.metrics_collector = metrics_collector
        self.max_workers = max_workers or config.global_settings.max_workers or 1
        self.byte_formatter = ByteFormatter()

    def run(
        self,
        tasks: Iterable[T],
        processor: Callable[[T], R],
        logger: LoggerPort,
        on_result: Optional[Callable[[R], None]] = None,
        post_callback: Optional[Callable[[List[R]], None]] = None,
    ) -> ExecutionResult[R]:
        logger.log(f"worker pool start {processor.__qualname__}", level="info")

        results: List[R] = []
        queue: Queue = Queue(self.config.global_settings.queue_size)
        lock = threading.Lock()
        sentinel = object()

        start_time = time.time()

        def worker(worker_id: str) -> None:
            logger.log("work started", level="info", worker_id=worker_id)
            while True:
                item = queue.get()
                if item is sentinel:
                    queue.task_done()
                    return
                try:
                    logger.log(f"running {item} {processor.__qualname__}", level="info")
                    result = processor(item)
                    self.metrics_collector.record_processing_bytes(
                        len(json.dumps(result, default=str).encode("utf-8"))
                    )
                    with lock:
                        results.append(result)
                        if callable(on_result):
                            on_result(result)

                    logger.log(
                        f"task processed {item}", level="info", worker_id=worker_id
                    )
                except Exception as exc:  # noqa: BLE001
                    logger.log(
                        f"worker error: {exc}", level="warning", worker_id=worker_id
                    )
                finally:
                    queue.task_done()

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            logger.log("ThreadPoolExecutor started", level="info")
            futures = [
                executor.submit(worker, uuid.uuid4().hex[:8])
                for _ in range(self.max_workers)
            ]

            for task in tasks:
                queue.put(task)

            for _ in range(self.max_workers):
                logger.log("sentinel in queue", level="info")
                queue.put(sentinel)

            queue.join()

        logger.log("ThreadPoolExecutor finished", level="info")

        for f in futures:
            f.result()

        elapsed = time.time() - start_time
        metrics = self.metrics_collector.get_metrics(elapsed_time=elapsed)

        if callable(post_callback):
            logger.log("Callable found", level="info")
            post_callback(results)

        logger.log(
            f"Executed {len(results)} tasks in {elapsed:.2f}s ("
            f"{self.byte_formatter.format_bytes(self.metrics_collector.processing_bytes)})",
            level="info",
        )

        return ExecutionResult(items=results, metrics=metrics)
