"""Use case responsible for fetching statement rows from the source."""

from __future__ import annotations

from typing import Iterable, List

from domain.dto import NsdDTO, StatementRowsDTO
from domain.ports import LoggerPort, StatementSourcePort


class FetchStatementsUseCase:
    """Retrieve parsed statement rows from the source port."""

    def __init__(self, logger: LoggerPort, source: StatementSourcePort) -> None:
        """Store dependencies and emit startup log."""
        self.logger = logger
        self.source = source
        self.logger.log("Start FetchStatementsUseCase", level="info")

    def run(self, batch: Iterable[NsdDTO]) -> List[StatementRowsDTO]:
        """Fetch all statements for the provided NSDs."""
        rows: List[StatementRowsDTO] = []
        for item in batch:
            self.logger.log(f"Fetch {item.nsd}", level="info")
            rows.append(self.source.fetch(item))
        return rows
