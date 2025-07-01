"""SQLite-backed repository implementation for NSD data."""

from __future__ import annotations

from typing import List

from domain.dto.nsd_dto import NsdDTO
from domain.ports import LoggerPort, NSDRepositoryPort
from infrastructure.config import Config
from infrastructure.models.nsd_model import NSDModel
from infrastructure.repositories import BaseRepository


class SQLiteNSDRepository(BaseRepository[NsdDTO], NSDRepositoryPort):
    """Concrete repository for NsdDTO using SQLite via SQLAlchemy."""

    def __init__(self, config: Config, logger: LoggerPort):
        super().__init__(config, logger)

    def save_all(self, items: List[NsdDTO]) -> None:
        """Persist a list of ``CompanyDTO`` objects."""
        session = self.Session()
        try:
            models = [NSDModel.from_dto(dto) for dto in items]
            for model in models:
                session.merge(model)
            session.commit()
            self.logger.log(
                f"Saved {len(items)} nsd records",
                level="info",
            )
        except Exception as e:
            session.rollback()
            self.logger.log(
                f"Failed to save nsd records: {e}",
                level="error",
            )
            raise
        finally:
            session.close()

    def get_all(self) -> List[NsdDTO]:
        session = self.Session()
        try:
            results = session.query(NSDModel).all()
            return [obj.to_dto() for obj in results]
        finally:
            session.close()

    def has_item(self, identifier: str) -> bool:
        """Checks if an item with the specified identifier exists in the
        database.

        Args:
            identifier (str): The unique identifier of the item to check.

        Returns:
            bool: True if the item exists, False otherwise.
        """
        session = self.Session()
        try:
            return session.query(NSDModel).filter_by(nsd=identifier).first() is not None
        finally:
            session.close()

    def get_by_id(self, id: str) -> NsdDTO:
        """Fetches an NSD record from the database by its unique identifier.

        Args:
            id (str): The unique identifier (ticker) of the NSD to retrieve.
        Returns:
            NsdDTO: Data transfer object representing the retrieved NSD.
        Raises:
            ValueError: If no NSD with the specified identifier is found.
        """
        session = self.Session()
        try:
            obj = session.query(NSDModel).filter_by(nsd=id).first()
            if not obj:
                raise ValueError(f"NSD not found: {id}")
            return obj.to_dto()
        finally:
            session.close()

    def get_all_primary_keys(self) -> set[int]:
        """Retrieve all distinct primary key values from the NSDModel table.

        Returns: All unique primary key values (nsd) from the NSDModel table.
        """
        session = self.Session()
        try:
            results = session.query(NSDModel.nsd).distinct().all()
            return {row[0] for row in results if row[0]}
        finally:
            session.close()
