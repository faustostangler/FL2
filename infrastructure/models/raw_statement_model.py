from __future__ import annotations

from domain.dto.raw_statement_dto import RawStatementDTO

from .abstract_statement_model import AbstractStatementModel


class RawStatementModel(AbstractStatementModel):
    """ORM model for raw statement rows."""

    __tablename__ = "tbl_raw_statements"

    @staticmethod
    def from_dto(dto: RawStatementDTO) -> "RawStatementModel":
        return RawStatementModel(**RawStatementModel._kwargs_from_dto(dto))

    def to_dto(self) -> RawStatementDTO:
        return RawStatementDTO(**self._dto_kwargs())
