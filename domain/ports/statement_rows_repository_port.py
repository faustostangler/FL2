from __future__ import annotations

from abc import ABC

from domain.dto.statement_rows_dto import StatementRowsDTO

from .base_repository_port import BaseRepositoryPort


class StatementRowsRepositoryPort(BaseRepositoryPort[StatementRowsDTO], ABC):
    """Port for persisting raw statement rows."""
