from __future__ import annotations

from domain.dto import StatementDTO
from domain.dto.statement_rows_dto import StatementRowsDTO
from domain.ports import LoggerPort
from domain.utils.statement_processing import classify_section


class ParseAndClassifyStatementsUseCase:
    """Parse raw HTML and build :class:`StatementDTO` objects."""

    def __init__(self, logger: LoggerPort) -> None:
        self.logger = logger

        self.logger.log(f"Start Class {self.__class__.__name__}", level="info")

    def run(self, row: StatementRowsDTO) -> StatementDTO:
        """Build a :class:`StatementDTO` from a statement row."""
        return StatementDTO(
            batch_id=str(row.nsd),
            account=row.account,
            section=classify_section(row.account),
            value=float(row.value),
            company=row.company_name,
            period=row.quarter,
        )
