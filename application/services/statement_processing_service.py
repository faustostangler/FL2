"""Service layer for processing financial statements."""

from __future__ import annotations

from typing import Iterable, List, Set, Tuple

from application.usecases.fetch_statements import FetchStatementsUseCase
from application.usecases.parse_and_classify_statements import (
    ParseAndClassifyStatementsUseCase,
)
from application.usecases.persist_statements import PersistStatementsUseCase
from domain.dto import StatementDTO, WorkerTaskDTO
from domain.dto.nsd_dto import NsdDTO
from domain.ports import (
    CompanyRepositoryPort,
    LoggerPort,
    NSDRepositoryPort,
    StatementRepositoryPort,
)
from infrastructure.config import Config
from infrastructure.helpers import MetricsCollector, WorkerPool


class StatementProcessingService:
    """Orchestrates fetching, parsing, and persisting statements."""

    def __init__(
        self,
        logger: LoggerPort,
        fetch_usecase: FetchStatementsUseCase,
        parse_usecase: ParseAndClassifyStatementsUseCase,
        persist_usecase: PersistStatementsUseCase,
        company_repo: CompanyRepositoryPort,
        nsd_repo: NSDRepositoryPort,
        statement_repo: StatementRepositoryPort,
        config: Config,
        max_workers: int = 1,
    ) -> None:
        """Initialize the service with its dependencies."""
        self.logger = logger
        self.fetch_usecase = fetch_usecase
        self.parse_usecase = parse_usecase
        self.persist_usecase = persist_usecase
        self.company_repo = company_repo
        self.nsd_repo = nsd_repo
        self.statement_repo = statement_repo
        self.config = config
        self.max_workers = max_workers
        self.logger.log("Start StatementProcessingService", level="info")

    def _build_targets(self) -> List[NsdDTO]:
        """Return NSD identifiers for statements that haven't been
        processed."""
        company_records = self.company_repo.get_all()
        nsd_records = self.nsd_repo.get_all()

        if not company_records or not nsd_records:
            return []

        processed = self.statement_repo.get_all_primary_keys()
        valid_types = set(self.config.domain.statements_types)

        company_names = {c.company_name for c in company_records if c.company_name}
        nsd_company_names = {n.company_name for n in nsd_records if n.company_name}
        common_company_names = sorted(set(company_names.intersection(nsd_company_names)))

        results = [
                n
                for n in nsd_records
                if (
                    n.nsd_type in valid_types
                    and n.company_name in common_company_names
                    and str(n.nsd) not in processed
                )
            ]

        results_sorted = sorted(results, key=lambda n: (n.company_name, n.quarter, n.nsd))

        return results_sorted


    def process_all(self, batch_nsd: List[NsdDTO]) -> None:
        """Fetch, parse, and persist statements for all batch IDs."""
        collector = MetricsCollector()

        # Queue 1: fetch HTML content
        fetch_pool = WorkerPool(
            config=self.config,
            metrics_collector=collector,
            max_workers=self.max_workers,
        )

        fetch_tasks = list(enumerate(batch_nsd))

        def fetch_processor(task: WorkerTaskDTO) -> tuple[str, str]:
            bid = task.data
            html = self.fetch_usecase.source.fetch(bid)
            return (bid, html)

        fetch_result = fetch_pool.run(
            tasks=fetch_tasks,
            processor=fetch_processor,
            logger=self.logger,
        )

        # Queue 2: parse statements
        parse_pool = WorkerPool(
            config=self.config,
            metrics_collector=collector,
            max_workers=self.max_workers,
        )

        parse_tasks = list(enumerate(fetch_result.items))

        def parse_processor(task: WorkerTaskDTO) -> List[StatementDTO]:
            bid, html = task.data
            return self.parse_usecase.run(bid, html)

        parse_result = parse_pool.run(
            tasks=parse_tasks,
            processor=parse_processor,
            logger=self.logger,
        )

        # Queue 3: persist statements
        persist_pool = WorkerPool(
            config=self.config,
            metrics_collector=collector,
            max_workers=self.max_workers,
        )

        persist_tasks = list(enumerate(parse_result.items))

        def persist_processor(task: WorkerTaskDTO) -> None:
            self.persist_usecase.run(task.data)
            return None

        persist_pool.run(
            tasks=persist_tasks,
            processor=persist_processor,
            logger=self.logger,
        )

        self.logger.log("Finished StatementProcessingService", level="info")

    def run(self) -> None:
        """Build targets and process all statements."""
        batch_nsd = self._build_targets()
        if not batch_nsd:
            self.logger.log("No statements to process", level="info")
            return
        self.process_all(batch_nsd)
