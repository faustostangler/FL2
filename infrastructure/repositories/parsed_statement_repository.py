from __future__ import annotations

from typing import Tuple

from domain.dto import ParsedStatementDTO
from domain.ports import LoggerPort, SqlAlchemyParsedStatementRepositoryPort
from infrastructure.config import Config
from infrastructure.models.statement_model import StatementModel
from infrastructure.repositories.sqlalchemy_repository_base import (
    SqlAlchemyRepositoryBase,
)


class SqlAlchemyParsedStatementRepository(
    SqlAlchemyRepositoryBase[ParsedStatementDTO, str],
    SqlAlchemyParsedStatementRepositoryPort,
):
    """SQLite-backed repository for ``ParsedStatementDTO`` objects."""

    def __init__(self, config: Config, logger: LoggerPort) -> None:
        super().__init__(config, logger)

        self.config = config
        self.logger = logger

    def get_model_class(self) -> Tuple[type, tuple]:
        """Return the SQLAlchemy ORM model class managed by this repository.

        Returns:
            type: The model class associated with this repository.
        """
        return StatementModel, (
                StatementModel.nsd,
                StatementModel.company_name,
                StatementModel.quarter,
                StatementModel.version,
                StatementModel.grupo,
                StatementModel.quadro,
                StatementModel.account,
            )
