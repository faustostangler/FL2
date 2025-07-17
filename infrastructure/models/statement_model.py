from __future__ import annotations

from sqlalchemy import PrimaryKeyConstraint, String
from sqlalchemy.orm import Mapped, mapped_column

from domain.dto.parsed_statement_dto import ParsedStatementDTO

from .base_model import BaseModel


class StatementModel(BaseModel):
    """ORM model for financial statements."""

    __tablename__ = "tbl_statements"
    __table_args__ = (
        PrimaryKeyConstraint(
            "nsd",
            "company_name",
            "quarter",
            "version",
            "grupo",
            "quadro",
            "account",
            name="pk_raw_statements",
        ),
    )

    nsd: Mapped[str] = mapped_column(String, primary_key=True)
    company_name: Mapped[str | None] = mapped_column(primary_key=True)
    quarter: Mapped[str | None] = mapped_column(primary_key=True)
    version: Mapped[str | None] = mapped_column(primary_key=True)
    grupo: Mapped[str] = mapped_column(primary_key=True)
    quadro: Mapped[str] = mapped_column(primary_key=True)
    account: Mapped[str] = mapped_column(primary_key=True)
    description: Mapped[str] = mapped_column()
    value: Mapped[float] = mapped_column()

    @staticmethod
    def from_dto(dto: ParsedStatementDTO) -> "StatementModel":
        return StatementModel(
            nsd=dto.nsd,
            company_name=dto.company_name,
            quarter=dto.quarter,
            version=dto.version,
            grupo=dto.grupo,
            quadro=dto.quadro,
            account=dto.account,
            description=dto.description,
            value=dto.value,
        )

    def to_dto(self) -> ParsedStatementDTO:
        return ParsedStatementDTO(
            nsd=self.nsd,
            company_name=self.company_name,
            quarter=self.quarter,
            version=self.version,
            grupo=self.grupo,
            quadro=self.quadro,
            account=self.account,
            description=self.description,
            value=self.value,
        )
