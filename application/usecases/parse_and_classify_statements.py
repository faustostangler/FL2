from __future__ import annotations

from domain.dto import StatementDTO
from domain.dto.statement_rows_dto import StatementRowsDTO
from domain.ports import LoggerPort, StatementRepositoryPort
from domain.utils.statement_processing import classify_section
from infrastructure.config import Config
from infrastructure.helpers import SaveStrategy


class ParseAndClassifyStatementsUseCase:
    """Parse raw HTML and build :class:`StatementDTO` objects."""

    def __init__(
        self,
        logger: LoggerPort,
        repository: StatementRepositoryPort,
        config: Config,
    ) -> None:
        self.logger = logger
        self.repository = repository
        self.strategy: SaveStrategy[StatementDTO] = SaveStrategy(
            repository.save_all, config=config
        )

        # self.logger.log(f"Load Class {self.__class__.__name__}", level="info")

    def run(self, row: StatementRowsDTO) -> StatementDTO:
        """Build a :class:`StatementDTO` from a statement row."""
        dto = StatementDTO(
            batch_id=str(row.nsd),
            account=row.account,
            section=classify_section(row.account),
            value=float(row.value),
            company=row.company_name,
            period=row.quarter,
        )
        self.strategy.handle(dto)
        return dto

    def finalize(self) -> None:
        """Flush any buffered statements."""
        self.strategy.finalize()
