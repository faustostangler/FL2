"""Use case for converting raw statement rows into ``StatementDTO`` objects."""

from __future__ import annotations

from typing import List

from domain.dto import StatementDTO, StatementRowsDTO
from domain.ports import LoggerPort
from domain.utils.statement_processing import classify_section, normalize_value


class ParseAndClassifyStatementsUseCase:
    """Convert parsed statement rows into :class:`StatementDTO` objects."""

    def __init__(self, logger: LoggerPort) -> None:
        """Initialize with a logger instance."""
        self.logger = logger
        self.logger.log("Start ParseAndClassifyStatementsUseCase", level="info")

    def run(self, dto: StatementRowsDTO) -> List[StatementDTO]:
        """Build ``StatementDTO`` objects from parsed rows."""
        dtos: List[StatementDTO] = []
        batch_id = str(dto.nsd.nsd)
        for row in dto.rows:
            account = str(row.get("account", ""))
            value_raw = str(row.get("value", 0))
            statement = StatementDTO(
                batch_id=batch_id,
                account=account,
                section=classify_section(account),
                value=normalize_value(value_raw),
            )
            dtos.append(statement)
        return dtos
