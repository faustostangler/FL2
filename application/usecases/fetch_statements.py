from __future__ import annotations

from typing import Callable, Iterable, List, Optional, Tuple

from domain.dto.nsd_dto import NsdDTO
from domain.dto.statement_rows_dto import StatementRowsDTO
from domain.dto.worker_class_dto import WorkerTaskDTO
from domain.ports import LoggerPort, StatementSourcePort
from infrastructure.config import Config
from infrastructure.helpers import MetricsCollector, SaveStrategy, WorkerPool


class FetchStatementsUseCase:
    """Retrieve raw HTML statements from the source port."""

    def __init__(
        self,
        logger: LoggerPort,
        source: StatementSourcePort,
        config: Config,
        max_workers: int = 1,
    ) -> None:
        self.logger = logger
        self.source = source
        self.config = config
        self.max_workers = max_workers
        self.logger.log("Start FetchStatementsUseCase", level="info")

    def fetch_all(
        self,
        targets: List[NsdDTO],
        save_callback: Optional[
            Callable[[List[Tuple[NsdDTO, List[StatementRowsDTO]]]], None]
        ] = None,
        threshold: Optional[int] = None,
    ) -> List[Tuple[NsdDTO, List[StatementRowsDTO]]]:
        """Fetch statements for ``targets`` concurrently."""
        collector = MetricsCollector()
        pool = WorkerPool(
            config=self.config,
            metrics_collector=collector,
            max_workers=self.max_workers,
        )

        strategy: SaveStrategy[Tuple[NsdDTO, List[StatementRowsDTO]]] = SaveStrategy(
            save_callback, threshold, config=self.config
        )

        tasks = list(enumerate(targets))

        def processor(task: WorkerTaskDTO) -> Tuple[NsdDTO, List[StatementRowsDTO]]:
            return self.source.fetch(task.data)

        def handle_batch(item: Tuple[NsdDTO, List[StatementRowsDTO]]) -> None:
            strategy.handle(item)

        result = pool.run(
            tasks=tasks,
            processor=processor,
            logger=self.logger,
            on_result=handle_batch,
        )

        strategy.finalize()

        return result.items

    def run(
        self,
        batch_rows: Iterable[NsdDTO],
        save_callback: Optional[
            Callable[[List[Tuple[NsdDTO, List[StatementRowsDTO]]]], None]
        ] = None,
        threshold: Optional[int] = None,
    ) -> List[Tuple[NsdDTO, List[StatementRowsDTO]]]:
        """Execute the use case for ``batch_rows``."""
        targets = list(batch_rows)
        if not targets:
            return []

        return self.fetch_all(
            targets=targets,
            save_callback=save_callback,
            threshold=threshold,
        )
