from __future__ import annotations

from typing import Callable, Iterable, List, Optional, Tuple

from domain.dto.nsd_dto import NsdDTO
from domain.dto.statement_rows_dto import StatementRowsDTO
from domain.dto.worker_class_dto import WorkerTaskDTO
from domain.ports import (
    LoggerPort,
    StatementRowsRepositoryPort,
    StatementSourcePort,
)
from infrastructure.config import Config
from infrastructure.helpers import MetricsCollector, SaveStrategy, WorkerPool


class FetchStatementsUseCase:
    """Retrieve raw HTML statements from the source port."""

    def __init__(
        self,
        logger: LoggerPort,
        source: StatementSourcePort,
        repository: StatementRowsRepositoryPort,
        config: Config,
        max_workers: int = 1,
    ) -> None:
        self.logger = logger
        self.source = source
        self.repository = repository
        self.config = config
        self.max_workers = max_workers

        self.logger.log(f"Load Class {self.__class__.__name__}", level="info")

    def fetch_all(
        self,
        targets: List[NsdDTO],
        repository: StatementRowsRepositoryPort,
        save_callback: Optional[
            Callable[[List[Tuple[NsdDTO, List[StatementRowsDTO]]]], None]
        ] = None,
        threshold: Optional[int] = None,
    ) -> List[Tuple[NsdDTO, List[StatementRowsDTO]]]:
        """Fetch statements for ``targets`` concurrently."""

        self.logger.log(
            "Run  Method controller.run()._statement_service().statements_fetch_service.run().fetch_usecase.run().fetch_all(save_callback, threshold)",
            level="info",
        )

        # Set up a metrics collector to track progress.
        self.logger.log("Instantiate collector", level="info")
        collector = MetricsCollector()
        self.logger.log("End Instance collector", level="info")

        # Create the worker pool responsible for parallel fetching.
        self.logger.log("Instantiate worker_pool", level="info")
        worker_pool = WorkerPool(
            config=self.config,
            metrics_collector=collector,
            max_workers=self.max_workers,
        )
        self.logger.log("End Instance worker_pool", level="info")

        # Initialize the saving strategy that buffers results.
        self.logger.log("Instantiate strategy", level="info")
        strategy: SaveStrategy[Tuple[NsdDTO, List[StatementRowsDTO]]] = SaveStrategy(
            lambda batch: self._save_batch(batch, repository, save_callback),
            threshold,
            config=self.config,
        )
        self.logger.log("End Instance strategy", level="info")

        # Pair each target with its index for worker pool processing.
        tasks = list(enumerate(targets))

        def processor(task: WorkerTaskDTO) -> Tuple[NsdDTO, List[StatementRowsDTO]]:
            self.logger.log(
                "Call Method controller.run()._statement_service().statements_fetch_service.run().fetch_usecase.run().fetch_all().processor().source.fetch()",
                level="info",
            )
            # <<<<<<< codex/double-check-result-handling-in-strategy-and-save-method
            fetched = self.source.fetch(task.data)
            # =======
            #             results = self.source.fetch(task.data)
            # >>>>>>> 2025-07-03-Statements-Round-1
            self.logger.log(
                "End  Method controller.run()._statement_service().statements_fetch_service.run().fetch_usecase.run().fetch_all().processor().source.fetch()",
                level="info",
            )

            # <<<<<<< codex/double-check-result-handling-in-strategy-and-save-method
            return fetched["nsd"], fetched["statements"]

        def handle_batch(item: Tuple[NsdDTO, List[StatementRowsDTO]]) -> None:
            if item[1]:
                # =======
                #             return results

                #         def handle_batch(item: Tuple[NsdDTO, List[StatementRowsDTO]]) -> None:
                #             if item["statements"]:
                # >>>>>>> 2025-07-03-Statements-Round-1
                self.logger.log(
                    "Call Method controller.run()._statement_service().statements_fetch_service.run().fetch_usecase.run().fetch_all().strategy.handle()",
                    level="info",
                )
                # <<<<<<< codex/double-check-result-handling-in-strategy-and-save-method
                strategy.handle(item)
                # =======
                #                 strategy.handle(item["statements"])
                # >>>>>>> 2025-07-03-Statements-Round-1
                self.logger.log(
                    "Call Method controller.run()._statement_service().statements_fetch_service.run().fetch_usecase.run().fetch_all().strategy.handle()",
                    level="info",
                )

        self.logger.log(
            "Call Method controller.run()._statement_service().statements_fetch_service.run().fetch_usecase.run().fetch_all().worker_pool.run(tasks, processor, handle_batch)",
            level="info",
        )
        result = worker_pool.run(
            tasks=tasks,
            processor=processor,
            logger=self.logger,
            on_result=handle_batch,
        )
        self.logger.log(
            "End  Method controller.run()._statement_service().statements_fetch_service.run().fetch_usecase.run().fetch_all().worker_pool.run(tasks, processor, handle_batch)",
            level="info",
        )

        strategy.finalize()

        self.logger.log(
            "End  Method controller.run()._statement_service().statements_fetch_service.run().fetch_usecase.run().fetch_all(save_callback, threshold)",
            level="info",
        )

        return result.items

    def _save_batch(
        self,
        batch: List[Tuple[NsdDTO, List[StatementRowsDTO]]],
        repository: StatementRowsRepositoryPort,
        user_callback: Optional[
            Callable[[List[Tuple[NsdDTO, List[StatementRowsDTO]]]], None]
        ] = None,
    ) -> None:
        rows: List[StatementRowsDTO] = [row for _, rows in batch for row in rows]
        if rows:
            repository.save_all(rows)
        if callable(user_callback):
            user_callback(batch)

    def run(
        self,
        batch_rows: Iterable[NsdDTO],
        save_callback: Optional[
            Callable[[List[Tuple[NsdDTO, List[StatementRowsDTO]]]], None]
        ] = None,
        threshold: Optional[int] = None,
    ) -> List[Tuple[NsdDTO, List[StatementRowsDTO]]]:
        """Execute the use case for ``batch_rows``."""

        self.logger.log(
            "Run  Method controller.run()._statement_service().statements_fetch_service.run().fetch_usecase.run(save_callback, threshold)",
            level="info",
        )

        targets = list(batch_rows)
        if not targets:
            return []

        self.logger.log(
            "Call Method controller.run()._statement_service().statements_fetch_service.run().fetch_usecase.run().fetch_all(save_callback, threshold)",
            level="info",
        )
        results = self.fetch_all(
            targets=targets,
            repository=self.repository,
            save_callback=save_callback,
            threshold=threshold,
        )
        self.logger.log(
            "End  Method controller.run()._statement_service().statements_fetch_service.run().fetch_usecase.run().fetch_all(save_callback, threshold)",
            level="info",
        )

        self.logger.log(
            "End  Method controller.run()._statement_service().statements_fetch_service.run().fetch_usecase.run(save_callback, threshold)",
            level="info",
        )

        return results
