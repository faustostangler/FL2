from __future__ import annotations

from typing import List

from domain.dto.statement_rows_dto import StatementRowsDTO
from domain.ports import LoggerPort, StatementRowsRepositoryPort
from infrastructure.config import Config
from infrastructure.models.statement_raw_model import StatementRawModel
from infrastructure.repositories.base_repository import BaseRepository


class SqlAlchemyStatementRowsRepository(
    BaseRepository[StatementRowsDTO], StatementRowsRepositoryPort
):
    """SQLite-backed repository for ``StatementRowsDTO`` objects."""

    def __init__(self, config: Config, logger: LoggerPort):
        super().__init__(config, logger)
        self.logger.log(f"Load Class {self.__class__.__name__}", level="info")

    def save_all(self, items: List[StatementRowsDTO]) -> None:
        session = self.Session()
        try:
            for dto in items:
                session.add(StatementRawModel.from_dto(dto))
            session.commit()
            self.logger.log(f"Saved {len(items)} raw statements", level="info")
        except Exception as exc:  # noqa: BLE001
            session.rollback()
            self.logger.log(f"Failed to save raw statements: {exc}", level="error")
            raise
        finally:
            session.close()

    def get_all(self) -> List[StatementRowsDTO]:
        session = self.Session()
        try:
            records = session.query(StatementRawModel).all()
            return [r.to_dto() for r in records]
        finally:
            session.close()

    def has_item(self, identifier: str) -> bool:
        session = self.Session()
        try:
            return (
                session.query(StatementRawModel).filter_by(id=int(identifier)).first()
                is not None
            )
        finally:
            session.close()

    def get_by_id(self, id: str) -> StatementRowsDTO:
        session = self.Session()
        try:
            obj = session.query(StatementRawModel).filter_by(id=int(id)).first()
            if not obj:
                raise ValueError(f"Raw statement not found: {id}")
            return obj.to_dto()
        finally:
            session.close()

    def get_all_primary_keys(self) -> set[str]:
        session = self.Session()
        try:
            ids = session.query(StatementRawModel.id).distinct().all()
            return {str(row[0]) for row in ids if row[0] is not None}
        finally:
            session.close()
