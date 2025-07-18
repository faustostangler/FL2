from __future__ import annotations

from sqlalchemy import PrimaryKeyConstraint, String
from sqlalchemy.orm import Mapped, mapped_column

from .base_model import BaseModel


class AbstractStatementModel(BaseModel):
    """Base ORM model for raw and parsed statement rows."""

    __abstract__ = True
    __table_args__ = (
        PrimaryKeyConstraint(
            "nsd",
            "company_name",
            "quarter",
            "version",
            "grupo",
            "quadro",
            "account",
            name="pk_statements_temp",
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

    _FIELDS = (
        "nsd",
        "company_name",
        "quarter",
        "version",
        "grupo",
        "quadro",
        "account",
        "description",
        "value",
    )

    @classmethod
    def _kwargs_from_dto(cls, dto: object) -> dict:
        return {field: getattr(dto, field) for field in cls._FIELDS}

    def _dto_kwargs(self) -> dict:
        return {field: getattr(self, field) for field in self._FIELDS}
