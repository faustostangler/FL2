from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from typing import Iterable, List

from application.usecases.fetch_statements import FetchStatementsUseCase
from application.usecases.parse_and_classify_statements import (
    ParseAndClassifyStatementsUseCase,
)
from application.usecases.persist_statements import PersistStatementsUseCase
from domain.dto import StatementDTO
from domain.ports import LoggerPort


class StatementProcessingService:
    """Orchestrates fetching, parsing, and persisting statements."""

    def __init__(
        self,
        logger: LoggerPort,
        fetch_usecase: FetchStatementsUseCase,
        parse_usecase: ParseAndClassifyStatementsUseCase,
        persist_usecase: PersistStatementsUseCase,
        max_workers: int = 4,
    ) -> None:
        self.logger = logger
        self.fetch_usecase = fetch_usecase
        self.parse_usecase = parse_usecase
        self.persist_usecase = persist_usecase
        self.max_workers = max_workers
        self.logger.log("Start StatementProcessingService", level="info")

    def process_all(self, batch_ids: Iterable[str]) -> None:
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Stage 1: fetch html in parallel
            fetch_futures = {
                executor.submit(self.fetch_usecase.source.fetch, bid): bid
                for bid in batch_ids
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
