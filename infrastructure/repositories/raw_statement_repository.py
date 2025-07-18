from __future__ import annotations

from typing import Tuple

from domain.dto.raw_statement_dto import RawStatementDTO
from domain.ports import LoggerPort, SqlAlchemyRawStatementRepositoryPort
from infrastructure.config import Config
from infrastructure.models.raw_statement_model import RawStatementModel
from infrastructure.repositories.sqlalchemy_repository_base import (
    SqlAlchemyRepositoryBase,
)


class SqlAlchemyRawStatementRepository(
    SqlAlchemyRepositoryBase[RawStatementDTO, str],
    SqlAlchemyRawStatementRepositoryPort,
):
    """SQLite-backed repository for ``RawStatementDTO`` objects."""

    def __init__(self, config: Config, logger: LoggerPort) -> None:
        super().__init__(config, logger)

        self.config = config
        self.logger = logger

    def get_model_class(self) -> Tuple[type, tuple]:
        """Return the SQLAlchemy ORM model class managed by this repository.

        Returns:
            type: The model class associated with this repository.
        """
        return RawStatementModel, (
            RawStatementModel.nsd,
            RawStatementModel.company_name,
            RawStatementModel.quarter,
            RawStatementModel.version,
            RawStatementModel.grupo,
            RawStatementModel.quadro,
            RawStatementModel.account,
        )
