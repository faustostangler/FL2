from __future__ import annotations

from typing import List

from bs4 import BeautifulSoup

from domain.dto import StatementDTO
from domain.ports import LoggerPort
from domain.utils.statement_processing import classify_section, normalize_value


class ParseAndClassifyStatementsUseCase:
    """Parse raw HTML and build :class:`StatementDTO` objects."""

    def __init__(self, logger: LoggerPort) -> None:
        self.logger = logger
        self.logger.log("Start ParseAndClassifyStatementsUseCase", level="info")

    def run(self, batch_id: str, html: str) -> List[StatementDTO]:
        soup = BeautifulSoup(html, "html.parser")
        dtos: List[StatementDTO] = []
        for row in soup.select("tr"):
            cells = [c.get_text(strip=True) for c in row.find_all("td")]
            if len(cells) < 2:
                continue
            account, value_raw = cells[0], cells[1]
            dto = StatementDTO(
                batch_id=batch_id,
                account=account,
                section=classify_section(account),
                value=normalize_value(value_raw),
            )
            dtos.append(dto)
        return dtos
