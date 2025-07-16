"""SQLite-backed repository implementation for NSD data."""

from __future__ import annotations

from typing import Tuple

from domain.dto.nsd_dto import NsdDTO
from domain.ports import LoggerPort, NSDRepositoryPort
from infrastructure.config import Config
from infrastructure.models.nsd_model import NSDModel
from infrastructure.repositories.sqlalchemy_repository_base import (
    SqlAlchemyRepositoryBase,
)


class SqlAlchemyNsdRepository(SqlAlchemyRepositoryBase[NsdDTO, int], NSDRepositoryPort):
    """Concrete repository for NsdDTO using SQLite via SQLAlchemy."""

    def __init__(self, config: Config, logger: LoggerPort) -> None:
        super().__init__(config, logger) 

        self.config = config
        self.logger = logger

    def get_model_class(self) -> Tuple:
        """Return the SQLAlchemy ORM model class managed by this repository.

        Returns:
            type: The model class associated with this repository.
        """
        return NSDModel, NSDModel.nsd

