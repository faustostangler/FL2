from __future__ import annotations

from sqlalchemy.orm import Mapped, mapped_column

from domain.dto.statement_rows_dto import StatementRowsDTO

from .base_model import BaseModel


class StatementRawModel(BaseModel):
    """ORM model for raw statement rows."""

    __tablename__ = "tbl_statements_raw"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nsd: Mapped[int] = mapped_column()
    company_name: Mapped[str | None] = mapped_column()
    quarter: Mapped[str | None] = mapped_column()
    version: Mapped[str | None] = mapped_column()
    grupo: Mapped[str] = mapped_column()
    quadro: Mapped[str] = mapped_column()
    account: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column()
    value: Mapped[float] = mapped_column()

    @staticmethod
    def from_dto(dto: StatementRowsDTO) -> "StatementRawModel":
        return StatementRawModel(
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
