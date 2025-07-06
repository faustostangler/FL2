from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass(frozen=True)
class StatementRowsDTO:
    """Immutable DTO for parsed statement rows."""

    nsd: int
    company_name: Optional[str]
    quarter: Optional[str]
    version: Optional[str]
    grupo: str
    quadro: str
    account: str
    description: str
    value: float

    @staticmethod
    def from_tuple(values: Tuple) -> "StatementRowsDTO":
        """Create a ``StatementRowsDTO`` from an ordered tuple."""
        (
            nsd,
            company_name,
            quarter,
            version,
            grupo,
            quadro,
            account,
            description,
            value,
        ) = values
        return StatementRowsDTO(
            nsd=int(nsd),
            company_name=str(company_name) if company_name is not None else None,
            quarter=str(quarter) if quarter is not None else None,
            version=str(version) if version is not None else None,
            grupo=str(grupo),
            quadro=str(quadro),
            account=str(account),
            description=str(description),
            value=float(value),
        )
