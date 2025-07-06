from __future__ import annotations

from typing import Iterable, List

from domain.dto.nsd_dto import NsdDTO
from domain.dto.statement_rows_dto import StatementRowsDTO
from domain.ports import LoggerPort, StatementSourcePort


class FetchStatementsUseCase:
    """Retrieve raw HTML statements from the source port."""

    def __init__(self, logger: LoggerPort, source: StatementSourcePort) -> None:
        self.logger = logger
        self.source = source
        self.logger.log("Start FetchStatementsUseCase", level="info")

    def run(
        self, batch_rows: Iterable[NsdDTO]
    ) -> List[tuple[NsdDTO, list[StatementRowsDTO]]]:
        results: List[tuple[NsdDTO, list[StatementRowsDTO]]] = []
        for row in batch_rows:
            self.logger.log(f"Fetch {row.nsd}", level="info")
            results.append(self.source.fetch(row))
        return results
