from __future__ import annotations

from sqlalchemy import PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column

from domain.dto.statement_rows_dto import StatementRowsDTO

from .base_model import BaseModel


class StatementRowsModel(BaseModel):
    """ORM model for raw statement rows."""

    __tablename__ = "tbl_raw_statements"
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

    nsd: Mapped[int] = mapped_column(primary_key=True)
    company_name: Mapped[str | None] = mapped_column(primary_key=True)
    quarter: Mapped[str | None] = mapped_column(primary_key=True)
    version: Mapped[str | None] = mapped_column(primary_key=True)
    grupo: Mapped[str] = mapped_column(primary_key=True)
    quadro: Mapped[str] = mapped_column(primary_key=True)
    account: Mapped[str] = mapped_column(primary_key=True)
    description: Mapped[str] = mapped_column()
    value: Mapped[float] = mapped_column()

    @staticmethod
    def from_dto(dto: StatementRowsDTO) -> "StatementRowsModel":
        return StatementRowsModel(
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

    def to_dto(self) -> StatementRowsDTO:
        return StatementRowsDTO(
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
