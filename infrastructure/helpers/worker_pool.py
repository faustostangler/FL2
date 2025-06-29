from __future__ import annotations

import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, Iterable, List, Optional, TypeVar

from domain.ports import MetricsCollectorPort
from domain.ports.worker_pool_port import (
    ExecutionResultDTO,
    LoggerPort,
    WorkerPoolPort,
)
from infrastructure.config import Config
from infrastructure.helpers.byte_formatter import ByteFormatter

T = TypeVar("T")
R = TypeVar("R")


class WorkerPool(WorkerPoolPort):
    """Simple thread pool implementation tied to the domain ``WorkerPoolPort``."""

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
        tasks: Iterable[T],
        processor: Callable[[T], R],
        logger: LoggerPort,
        on_result: Optional[Callable[[R], None]] = None,
        post_callback: Optional[Callable[[List[R]], None]] = None,
    ) -> ExecutionResultDTO[R]:
        """Process ``tasks`` concurrently using ``processor``."""

        logger.log("Worker pool start", level="info")

        results: List[R] = []
        start_time = time.perf_counter()

        # Spawn a pool of threads to execute the processor function
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            logger.log("ThreadPoolExecutor started", level="info")
            # Map each submitted future back to its originating task
            future_to_task = {executor.submit(processor, task): task for task in tasks}

            for index, future in enumerate(as_completed(future_to_task)):
                future_to_task[future]
                try:
                    result = future.result()
                except Exception as exc:  # noqa: BLE001
                    logger.log(f"worker error: {exc}", level="warning")
                    continue

                logger.log(f"task processed {index}", level="info")
                self.metrics_collector.record_processing_bytes(
                    len(json.dumps(result, default=str).encode("utf-8"))
                )
                results.append(result)
                if callable(on_result):
                    on_result(result)
            logger.log("ThreadPoolExecutor finished", level="info")

        elapsed = time.perf_counter() - start_time
        # Package execution metrics (network and processing bytes)
        metrics = self.metrics_collector.get_metrics(elapsed_time=elapsed)

        if callable(post_callback):
            logger.log("Callable found", level="info")
            post_callback(results)

        logger.log(
            f"Executed {len(results)} tasks in {elapsed:.2f}s ("
            f"{self.byte_formatter.format_bytes(self.metrics_collector.processing_bytes)} {self.byte_formatter.format_bytes(self.metrics_collector.network_bytes)})",
            level="info",
        )

        return ExecutionResultDTO(items=results, metrics=metrics)
