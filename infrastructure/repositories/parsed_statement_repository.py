from __future__ import annotations

from typing import Any, List, Set

from domain.dto.statement_rows_dto import StatementRowsDTO
from domain.ports import LoggerPort, ParsedStatementRepositoryPort
from infrastructure.config import Config
from infrastructure.helpers.list_flattener import ListFlattener
from infrastructure.models.statement_rows_model import StatementRowsModel
from infrastructure.repositories.base_repository import BaseRepository


class SqlAlchemyParsedStatementRepository(
    BaseRepository[StatementRowsDTO], ParsedStatementRepositoryPort
):
    """SQLite-backed repository for ``StatementRowsDTO`` objects."""

    def __init__(self, config: Config, logger: LoggerPort) -> None:
        super().__init__(config, logger)
        # self.logger.log(f"Load Class {self.__class__.__name__}", level="info")

    def save_all(self, items: List[StatementRowsDTO]) -> None:
        session = self.Session()

        try:
            flat_items = ListFlattener.flatten(
                items
            )  # recebe nested lists, devolve flat list

            valid_items = [item for item in flat_items if item is not None]

            for dto in valid_items:
                session.merge(StatementRowsModel.from_dto(dto))
            session.commit()

            if len(valid_items) > 0:
                self.logger.log(
                    f"Saved {len(valid_items)} parsed statement rows", level="info"
                )
        except Exception as exc:  # noqa: BLE001
            session.rollback()
            self.logger.log(
                f"Failed to save parsed statement rows: {exc}", level="error"
            )
            raise
        finally:
            session.close()

    def get_all(self) -> List[StatementRowsDTO]:
        session = self.Session()
        try:
            records = session.query(StatementRowsModel).all()
            return [r.to_dto() for r in records]
        finally:
            session.close()

    def has_item(self, identifier: str) -> bool:
        session = self.Session()
        try:
            return (
                session.query(StatementRowsModel).filter_by(id=identifier).first()
                is not None
            )
        finally:
            session.close()

    def get_by_id(self, id: str) -> StatementRowsDTO:
        session = self.Session()
        try:
            obj = session.query(StatementRowsModel).filter_by(id=id).first()
            if not obj:
                raise ValueError(f"Raw statement not found: {id}")
            return obj.to_dto()
        finally:
            session.close()

    def get_all_primary_keys(self) -> set[str]:
        session = self.Session()
        try:
            rows = session.query(StatementRowsModel.nsd).distinct().all()
            results = {row[0] for row in rows if row[0] is not None}
            return results
        finally:
            session.close()

    def get_by_key(
        self,
        nsd: str,
        company_name: str,
        quarter: str,
        version: str,
        grupo: str,
        quadro: str,
        account: str,
    ) -> StatementRowsDTO:
        """Return exactly one raw row matching the full composite key.

        Raises if not found.
        """
        session = self.Session()
        try:
            model = session.query(StatementRowsModel).get(
                {
                    "nsd": nsd,
                    "company_name": company_name,
                    "quarter": quarter,
                    "version": version,
                    "grupo": grupo,
                    "quadro": quadro,
                    "account": account,
                }
            )
            if model is None:
                raise ValueError(f"No raw statement for key {nsd}, {company_name}, …")
            return model.to_dto()
        finally:
            session.close()

    def get_by_column(self, column_name: str, value: Any) -> List[StatementRowsDTO]:
        """Return all raw rows where `column_name == value`."""
        session = self.Session()
        try:
            # Dynamically get the column attribute from the model
            column_attr = getattr(StatementRowsModel, column_name)
            models = (
                session.query(StatementRowsModel).filter(column_attr == value).all()
            )
            return [m.to_dto() for m in models]
        finally:
            session.close()

    def get_existing_by_column(self, column_name: str) -> Set[Any]:
        """Return the distinct values for the given column in
        tbl_raw_statements.

        e.g. repo.get_existing_by_column("nsd") -> {94790, 12345, …}
        """
        session = self.Session()
        try:
            # dynamically access the ORM attribute
            column_attr = getattr(StatementRowsModel, column_name)
            rows = session.query(column_attr).distinct().all()
            results = {row[0] for row in rows if row[0] is not None}
            return results
        finally:
            session.close()
