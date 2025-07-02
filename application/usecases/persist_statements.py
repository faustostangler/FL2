from __future__ import annotations

from typing import List

from domain.dto import StatementDTO
from domain.ports import LoggerPort, StatementRepositoryPort


class PersistStatementsUseCase:
    """Persist statements via the repository port."""

    def __init__(self, logger: LoggerPort, repository: StatementRepositoryPort) -> None:
        self.logger = logger
        self.repository = repository
        self.logger.log("Start PersistStatementsUseCase", level="info")

    def run(self, statements: List[StatementDTO]) -> None:
        if not statements:
            return
        self.logger.log(f"Persisting {len(statements)} statements", level="info")
        self.repository.save_all(statements)
