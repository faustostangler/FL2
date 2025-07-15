from __future__ import annotations

from typing import List, Set

from domain.dto.statement_dto import StatementDTO
from domain.ports import LoggerPort, RawStatementRepositoryPort
from infrastructure.config import Config
from infrastructure.helpers.list_flattener import ListFlattener
from infrastructure.models.statement_model import StatementModel

from .base_repository import BaseRepository


class SqlAlchemyRawStatementRepository(
    BaseRepository[StatementDTO], RawStatementRepositoryPort
):
    """SQLite-backed repository for ``StatementDTO`` objects."""

    def __init__(self, config: Config, logger: LoggerPort) -> None:
        super().__init__(config, logger)

    def save_all(self, items: List[StatementDTO]) -> None:
        session = self.Session()
        try:
            flat_items = ListFlattener.flatten(
                items
            )  # recebe nested lists, devolve flat list

            valid_items = [item for item in flat_items if item is not None]

            for dto in valid_items:
                model = StatementModel.from_dto(dto)
                session.merge(model)
            session.commit()

            if len(valid_items) > 0:
                self.logger.log(
                    f"Saved {len(valid_items)} raw statement rows", level="info"
                )
        except Exception as exc:  # noqa: BLE001
            session.rollback()
            self.logger.log(f"Failed to save raw statements: {exc}", level="error")
            raise
        finally:
            session.close()

    def get_all(self) -> List[StatementDTO]:
        session = self.Session()
        try:
            records = session.query(StatementModel).all()
            return [r.to_dto() for r in records]
        finally:
            session.close()

    def has_item(self, identifier: int) -> bool:
        session = self.Session()
        try:
            return (
                session.query(StatementModel).filter_by(id=identifier).first()
                is not None
            )
        finally:
            session.close()

    def get_by_id(self, id: int) -> StatementDTO:
        session = self.Session()
        try:
            obj = session.query(StatementModel).filter_by(id=id).first()
            if not obj:
                raise ValueError(f"Statement not found: {id}")
            return obj.to_dto()
        finally:
            session.close()

    def get_all_primary_keys(self) -> Set[int]:
        """Retrieve the set of all primary keys already persisted."""
        raise NotImplementedError
