from __future__ import annotations

from typing import List

from domain.dto import StatementDTO
from domain.ports import LoggerPort, StatementRepositoryPort


class BaseStatementsUseCase:
    """Shared logic for statement-related use cases."""

    def __init__(self, repository: StatementRepositoryPort, logger: LoggerPort) -> None:
        self.repository = repository
        self.logger = logger

    def _persistir_lote(self, dtos: List[StatementDTO]) -> None:
        if not dtos:
            return
        try:
            self.repository.save_all(dtos)
            self.logger.log(f"Persistidos {len(dtos)} statements", level="info")
        except Exception:  # noqa: BLE001
            self.logger.log(
                "Falha ao persistir lote de statements", level="error", exc_info=True
            )
            raise
