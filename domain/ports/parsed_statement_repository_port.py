from __future__ import annotations

from domain.dto import ParsedStatementDTO

from .base_repository_port import SqlAlchemyRepositoryBasePort


class SqlAlchemyParsedStatementRepositoryPort(
    SqlAlchemyRepositoryBasePort[ParsedStatementDTO, int]
):
    """Port for persisting parsed statement rows."""
