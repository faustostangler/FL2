from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass(frozen=True)
class StatementRowsDTO:
    """Immutable DTO for parsed statement rows."""

    account: str
    description: str
    value: float
    grupo: str
    quadro: str
    company_name: Optional[str]
    nsd: int
    quarter: Optional[str]
    version: Optional[str]

    @staticmethod
    def from_tuple(values: Tuple) -> "StatementRowsDTO":
        """Create a ``StatementRowsDTO`` from an ordered tuple."""
        (
            account,
            description,
            value,
            grupo,
            quadro,
            company_name,
            nsd,
            quarter,
            version,
        ) = values
        return StatementRowsDTO(
            account=str(account),
            description=str(description),
            value=float(value),
            grupo=str(grupo),
            quadro=str(quadro),
            company_name=str(company_name) if company_name is not None else None,
            nsd=int(nsd),
            quarter=str(quarter) if quarter is not None else None,
            version=str(version) if version is not None else None,
        )
