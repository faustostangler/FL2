"""Service layer for processing financial statements."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from typing import Iterable, List, Set

from application.usecases.fetch_statements import FetchStatementsUseCase
from application.usecases.parse_and_classify_statements import (
    ParseAndClassifyStatementsUseCase,
)
from application.usecases.persist_statements import PersistStatementsUseCase
from domain.dto import StatementDTO
from domain.ports import (
    CompanyRepositoryPort,
    LoggerPort,
    NSDRepositoryPort,
    StatementRepositoryPort,
)
from infrastructure.config import Config


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

    def _build_targets(self) -> Set[str]:
        """Return NSD identifiers for statements that haven't been
        processed."""
        company_records = self.company_repo.get_all()
        nsd_records = self.nsd_repo.get_all()

        if not company_records or not nsd_records:
            return set()

        processed = self.statement_repo.get_all_primary_keys()
        valid_types = set(self.config.domain.statements_types)

        company_names = {c.company_name for c in company_records if c.company_name}
        nsd_company_names = {n.company_name for n in nsd_records if n.company_name}
        common_company_names = sorted(company_names.intersection(nsd_company_names))
        target_names = sorted(set(common_company_names))

        results = {
            str(n.nsd)
            for n in nsd_records
            if (
                n.nsd_type in valid_types
                and n.company_name in target_names
                and str(n.nsd) not in processed
            )
        }

        return results

    def process_all(self, batch_nsd: Iterable[str]) -> None:
        """Fetch, parse, and persist statements for all batch IDs."""
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Stage 1: fetch html in parallel
            fetch_futures = {
                executor.submit(self.fetch_usecase.source.fetch, bid): bid
                for bid in batch_nsd
            }
            html_results: List[tuple[str, str]] = []
            for fut in fetch_futures:
                batch = fetch_futures[fut]
                html_results.append((batch, fut.result()))

            # Stage 2: parse and classify in parallel
            parse_futures = {
                executor.submit(self.parse_usecase.run, bid, html): bid
                for bid, html in html_results
            }
            parsed: List[List[StatementDTO]] = []
            for fut in parse_futures:
                parsed.append(fut.result())

            # Stage 3: persist in parallel
            persist_futures = [
                executor.submit(self.persist_usecase.run, items) for items in parsed
            ]
            for fut in persist_futures:
                fut.result()

        self.logger.log("Finished StatementProcessingService", level="info")

    def run(self) -> None:
        """Build targets and process all statements."""
        batch_nsd = self._build_targets()
        if not batch_nsd:
            self.logger.log("No statements to process", level="info")
            return
        self.process_all(batch_nsd)
