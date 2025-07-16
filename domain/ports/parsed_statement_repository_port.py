from __future__ import annotations

from domain.dto import StatementDTO

from .base_repository_port import SqlAlchemyRepositoryBasePort


class SqlAlchemyParsedStatementRepositoryPort(SqlAlchemyRepositoryBasePort[StatementDTO, int]):
    """Port for persisting raw statement rows."""
