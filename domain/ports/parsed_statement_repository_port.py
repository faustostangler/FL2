from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Set

from domain.dto.statement_rows_dto import StatementRowsDTO

from .base_repository_port import SqlAlchemyRepositoryBasePort


class ParsedStatementRepositoryPort(SqlAlchemyRepositoryBasePort[StatementRowsDTO, int], ABC):
    """Port for persisting raw statement rows."""

    @abstractmethod
    def get_existing_by_column(self, column_name: str) -> Set[Any]:
        """Return distinct values for the provided column."""
        raise NotImplementedError
