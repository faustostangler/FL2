from __future__ import annotations

from abc import ABC
from typing import List

from domain.dto.statement_rows_dto import StatementRowsDTO

from .base_repository_port import BaseRepositoryPort


class StatementRowsRepositoryPort(BaseRepositoryPort[StatementRowsDTO], ABC):
    """Port for persisting raw statement rows."""

    def save_all(self, items: List[StatementRowsDTO]) -> None:  # type: ignore[override]
        raise NotImplementedError
