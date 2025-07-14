from __future__ import annotations

from typing import Callable, List, Optional, Tuple

from application.usecases.fetch_statements import FetchStatementsUseCase
from domain.dto import NsdDTO, StatementRowsDTO
from domain.ports import (
    CompanyRepositoryPort,
    LoggerPort,
    MetricsCollectorPort,
    NSDRepositoryPort,
    ParsedStatementRepositoryPort,
    RawStatementRepositoryPort,
    RawStatementSourcePort,
)
from infrastructure.config import Config
from infrastructure.helpers import WorkerPool


class StatementFetchService:
    """Fetch raw statements for pending NSDs."""

    def __init__(
        self,
        logger: LoggerPort,
        source: RawStatementSourcePort,
        parsed_statements_repo: ParsedStatementRepositoryPort,
        company_repo: CompanyRepositoryPort,
        nsd_repo: NSDRepositoryPort,
        raw_statement_repo: RawStatementRepositoryPort,
        config: Config,
        metrics_collector: MetricsCollectorPort,
        worker_pool_executor: WorkerPool,
        max_workers: int = 1,
    ) -> None:
        """Store dependencies for the service."""
        self.logger = logger
        self.parsed_statements_repo = parsed_statements_repo
        self.company_repo = company_repo
        self.nsd_repo = nsd_repo
        self.raw_statement_repo = raw_statement_repo
        self.config = config
        self.max_workers = max_workers
        self.collector = metrics_collector
        self.worker_pool_executor = worker_pool_executor

        self.fetch_usecase = FetchStatementsUseCase(
            logger=self.logger,
            source=source,
            parsed_statements_repo=parsed_statements_repo,
            raw_statement_repository=raw_statement_repo,
            metrics_collector=self.collector,
            worker_pool_executor=self.worker_pool_executor,
            config=self.config,
            max_workers=self.max_workers,
        )

        # self.logger.log(f"Load Class {self.__class__.__name__}", level="info")

    def _build_targets(self) -> List[NsdDTO]:
        """Return NSD identifiers that still need fetching."""
        # self.logger.log(
        #     "Run  Method controller.run()._statement_service().statements_fetch_service.run()._build_targets()",
        #     level="info",
        # )
        company_records = self.company_repo.get_all()
        nsd_records = self.nsd_repo.get_all()

        if not company_records or not nsd_records:
            return []

        processed = self.parsed_statements_repo.get_existing_by_column(
            column_name="nsd"
        )
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
                and n.nsd not in processed
            )
        ]

        _full_results = [
            n
            for n in nsd_records
            if (n.nsd_type in valid_types and n.company_name in common_company_names)
        ]
        # self.logger.log(f"results: {len(results)} full_results: {len(full_results)}")
        # self.logger.log(
        #     "End  Method controller.run()._statement_service().statements_fetch_service.run()._build_targets()",
        #     level="info",
        # )

        return sorted(results, key=lambda n: (n.company_name, n.quarter, n.nsd))

    def fetch_statements(
        self,
        save_callback: Optional[Callable[[List[StatementRowsDTO]], None]] = None,
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

        # self.logger.log(
        #     "Run  Method controller.run()._statement_service().statements_fetch_service.run()",
        #     level="info",
        # )

        # self.logger.log(
        #     "Call Method controller.run()._statement_service().statements_fetch_service.run()._build_targets()",
        #     level="info",
        # )
        targets = self._build_targets()
        # self.logger.log(
        #     "Run  Method controller.run()._statement_service().statements_fetch_service.run()._build_targets()",
        #     level="info",
        # )

        if not targets:
            # self.logger.log("No statements to fetch", level="info")
            return []

        # self.logger.log(
        #     "Call Method controller.run()._statement_service().statements_fetch_service.run().fetch_usecase.run(save_callback, threshold)",
        #     level="info",
        # )
        rows = self.fetch_usecase.fetch_statement_rows(
            batch_rows=targets,
            save_callback=save_callback,
            threshold=threshold,
        )
        # self.logger.log(
        #     "End  Method controller.run()._statement_service().statements_fetch_service.run().fetch_usecase.run(save_callback, threshold)",
        #     level="info",
        # )

        # self.logger.log(
        #     "End  Method controller.run()._statement_service().statements_fetch_service.run()",
        #     level="info",
        # )

        return rows
