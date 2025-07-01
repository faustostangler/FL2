from __future__ import annotations

from sqlalchemy.orm import Mapped, mapped_column

from domain.dto.statement_dto import StatementDTO

from .base_model import BaseModel


class StatementModel(BaseModel):
    """ORM model for financial statements."""

    __tablename__ = "tbl_statements"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    batch_id: Mapped[str] = mapped_column()
    account: Mapped[str] = mapped_column()
    section: Mapped[str] = mapped_column()
    value: Mapped[float] = mapped_column()
    company: Mapped[str | None] = mapped_column()
    period: Mapped[str | None] = mapped_column()

    @staticmethod
    def from_dto(dto: StatementDTO) -> "StatementModel":
        return StatementModel(
            batch_id=dto.batch_id,
            account=dto.account,
            section=dto.section,
            value=dto.value,
            company=dto.company,
            period=dto.period,
        )

    def to_dto(self) -> StatementDTO:
        return StatementDTO(
            batch_id=self.batch_id,
            account=self.account,
            section=self.section,
            value=self.value,
            company=self.company,
            period=self.period,
        )
