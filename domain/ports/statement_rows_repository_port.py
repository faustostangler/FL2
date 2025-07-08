from __future__ import annotations

from abc import ABC, abstractmethod

from domain.dto.statement_rows_dto import StatementRowsDTO

from .base_repository_port import BaseRepositoryPort


class StatementRowsRepositoryPort(BaseRepositoryPort[StatementRowsDTO], ABC):
    """Port for persisting raw statement rows."""

    @abstractmethod
    def get_existing_by_column(self, column_name: str) -> set[object]:
        """Return distinct values for ``column_name`` in the persistence
        layer."""
        raise NotImplementedError
