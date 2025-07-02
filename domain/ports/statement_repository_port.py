from __future__ import annotations

from abc import ABC
from typing import List

from domain.dto.statement_dto import StatementDTO

from .base_repository_port import BaseRepositoryPort


class StatementRepositoryPort(BaseRepositoryPort[StatementDTO], ABC):
    """Port for persisting parsed statements."""

    def save_all(self, items: List[StatementDTO]) -> None:
        raise NotImplementedError
