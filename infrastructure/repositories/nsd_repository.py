from typing import List

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from domain.dto.nsd_dto import NSDDTO
from infrastructure.config import Config
from infrastructure.logging import Logger
from infrastructure.models.nsd_model import Base, NSDModel
from infrastructure.repositories.base_repository import BaseRepository


class SQLiteNSDRepository(BaseRepository[NSDDTO]):
    """Concrete repository for NSDDTO using SQLite via SQLAlchemy."""

    def __init__(self, config: Config, logger: Logger):
        self.config = config
        self.logger = logger
        self.logger.log("Start SQLiteNSDRepository", level="info")

        self.engine = create_engine(
            config.database.connection_string,
            connect_args={"check_same_thread": False},
        )
        with self.engine.connect() as conn:
            conn.execute(text("PRAGMA journal_mode=WAL"))
        self.Session = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)

    def save_all(self, items: List[NSDDTO]) -> None:
        session = self.Session()
        try:
            models = [NSDModel.from_dto(dto) for dto in items]
            session.bulk_save_objects(models)
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

    def get_all(self) -> List[NSDDTO]:
        session = self.Session()
        try:
            results = session.query(NSDModel).all()
            return [obj.to_dto() for obj in results]
        finally:
            session.close()

    def has_item(self, identifier: str) -> bool:
        """
        Checks if an item with the specified identifier exists in the database.

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

    def get_by_id(self, id: str) -> NSDDTO:
        """
        Fetches an NSD record from the database by its unique identifier.
        Args:
            id (str): The unique identifier (ticker) of the NSD to retrieve.
        Returns:
            NSDDTO: Data transfer object representing the retrieved NSD.
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
        """
        Retrieve all distinct primary key values from the NSDModel table.

        Returns: All unique primary key values (nsd) from the NSDModel table.
        """
        session = self.Session()
        try:
            results = session.query(NSDModel.nsd).distinct().all()
            return {row[0] for row in results if row[0]}
        finally:
            session.close()
