from __future__ import annotations

from typing import Iterable, List

from domain.ports import LoggerPort, StatementSourcePort


class FetchStatementsUseCase:
    """Retrieve raw HTML statements from the source port."""

    def __init__(self, logger: LoggerPort, source: StatementSourcePort) -> None:
        self.logger = logger
        self.source = source
        self.logger.log("Start FetchStatementsUseCase", level="info")

    def run(self, batch_ids: Iterable[str]) -> List[str]:
        html_chunks: List[str] = []
        for batch_id in batch_ids:
            self.logger.log(f"Fetch {batch_id}", level="info")
            html_chunks.append(self.source.fetch(batch_id))
        return html_chunks
