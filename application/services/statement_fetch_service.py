from __future__ import annotations

from typing import Callable, List, Optional, Tuple

from application.usecases.fetch_statements import FetchStatementsUseCase
from domain.dto import NsdDTO, StatementRowsDTO, WorkerTaskDTO
from domain.ports import (
    CompanyRepositoryPort,
    LoggerPort,
    NSDRepositoryPort,
    StatementRepositoryPort,
)
from infrastructure.config import Config
from infrastructure.helpers import MetricsCollector, SaveStrategy, WorkerPool


class StatementFetchService:
    """Fetch raw statements for pending NSDs."""

    def __init__(
        self,
        logger: LoggerPort,
        fetch_usecase: FetchStatementsUseCase,
        company_repo: CompanyRepositoryPort,
        nsd_repo: NSDRepositoryPort,
        statement_repo: StatementRepositoryPort,
        config: Config,
        max_workers: int = 1,
    ) -> None:
        """Store dependencies for the service."""
        self.logger = logger
        self.fetch_usecase = fetch_usecase
        self.company_repo = company_repo
        self.nsd_repo = nsd_repo
        self.statement_repo = statement_repo
        self.config = config
        self.max_workers = max_workers
        self.logger.log("Start StatementFetchService", level="info")

    def _build_targets(self) -> List[NsdDTO]:
        """Return NSD identifiers that still need fetching."""
        company_records = self.company_repo.get_all()
        nsd_records = self.nsd_repo.get_all()

        if not company_records or not nsd_records:
            return []

        processed = self.statement_repo.get_all_primary_keys()
        valid_types = set(self.config.domain.statements_types)

        company_names = {c.company_name for c in company_records if c.company_name}
        nsd_company_names = {n.company_name for n in nsd_records if n.company_name}
        common_company_names = sorted(
            set(company_names.intersection(nsd_company_names))
        )

        results = [
            n
            for n in nsd_records
            if (
                n.nsd_type in valid_types
                and n.company_name in common_company_names
                and str(n.nsd) not in processed
            )
        ]

        return sorted(results, key=lambda n: (n.company_name, n.quarter, n.nsd))

    def fetch_all(
        self,
        targets: List[NsdDTO],
        save_callback: Optional[
            Callable[[List[Tuple[NsdDTO, List[StatementRowsDTO]]]], None]
        ] = None,
        threshold: Optional[int] = None,
    ) -> List[Tuple[NsdDTO, List[StatementRowsDTO]]]:
        """Fetch statements for ``targets`` concurrently.

        Parameters
        ----------
        targets:
            The NSD entries to fetch.
        save_callback:
            Optional function to persist buffered results.
        threshold:
            Number of items to collect before invoking ``save_callback``.
        """
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
            results = self.fetch_usecase.source.fetch(task.data)
            return results

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
        save_callback: Optional[
            Callable[[List[Tuple[NsdDTO, List[StatementRowsDTO]]]], None]
        ] = None,
        threshold: Optional[int] = None,
    ) -> List[Tuple[NsdDTO, List[StatementRowsDTO]]]:
        """Execute the fetch workflow and return raw rows.

        Parameters
        ----------
        save_callback:
            Optional function to persist buffered results.
        threshold:
            Number of items to collect before invoking ``save_callback``.
        """
        targets = self._build_targets()
        if not targets:
            self.logger.log("No statements to fetch", level="info")
            return []

        rows = self.fetch_all(targets, save_callback=save_callback, threshold=threshold)
        self.logger.log("Finished StatementFetchService", level="info")
        return rows
