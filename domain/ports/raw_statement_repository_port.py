from __future__ import annotations

from abc import ABC

from domain.dto.statement_dto import StatementDTO

from .base_repository_port import BaseRepositoryPort


class RawStatementRepositoryPort(BaseRepositoryPort[StatementDTO], ABC):
    """Port for persisting parsed statements."""
