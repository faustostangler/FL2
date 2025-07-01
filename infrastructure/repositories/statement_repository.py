from __future__ import annotations

from typing import List

from domain.dto.statement_dto import StatementDTO
from domain.ports import LoggerPort, StatementRepositoryPort
from infrastructure.config import Config
from infrastructure.models.statement_model import StatementModel
from infrastructure.repositories.base_repository import BaseRepository


class SqlAlchemyStatementRepository(
    BaseRepository[StatementDTO], StatementRepositoryPort
):
    """SQLite-backed repository for ``StatementDTO`` objects."""

    def __init__(self, config: Config, logger: LoggerPort):
        super().__init__(config, logger)

    def save_all(self, items: List[StatementDTO]) -> None:
        session = self.Session()
        try:
            for dto in items:
                session.merge(StatementModel.from_dto(dto))
            session.commit()
            self.logger.log(f"Saved {len(items)} statements", level="info")
        except Exception as exc:  # noqa: BLE001
            session.rollback()
            self.logger.log(f"Failed to save statements: {exc}", level="error")
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

    def has_item(self, identifier: str) -> bool:
        session = self.Session()
        try:
            return (
                session.query(StatementModel).filter_by(id=int(identifier)).first()
                is not None
            )
        finally:
            session.close()

    def get_by_id(self, id: str) -> StatementDTO:
        session = self.Session()
        try:
            obj = session.query(StatementModel).filter_by(id=int(id)).first()
            if not obj:
                raise ValueError(f"Statement not found: {id}")
            return obj.to_dto()
        finally:
            session.close()

    def get_all_primary_keys(self) -> set[str]:
        session = self.Session()
        try:
            ids = session.query(StatementModel.id).distinct().all()
            return {str(row[0]) for row in ids}
        finally:
            session.close()
