from __future__ import annotations

from domain.dto.parsed_statement_dto import ParsedStatementDTO

from .abstract_statement_model import AbstractStatementModel


class ParsedStatementModel(AbstractStatementModel):
    """ORM model for parsed statement rows."""

    __tablename__ = "tbl_parsed_statements"

    @staticmethod
    def from_dto(dto: ParsedStatementDTO) -> "ParsedStatementModel":
        return ParsedStatementModel(**ParsedStatementModel._kwargs_from_dto(dto))

    def to_dto(self) -> ParsedStatementDTO:
        return ParsedStatementDTO(**self._dto_kwargs())
