from __future__ import annotations

from abc import ABC

from domain.dto.raw_statement_dto import RawStatementDTO

from .base_repository_port import SqlAlchemyRepositoryBasePort


class SqlAlchemyRawStatementRepositoryPort(
    SqlAlchemyRepositoryBasePort[RawStatementDTO, str], ABC
):
    """Port for persisting raw statement rows."""
