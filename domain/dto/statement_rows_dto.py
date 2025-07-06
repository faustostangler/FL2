from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


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
# <<<<<<< HEAD
#     def from_tuple(values: Tuple) -> "StatementRowsDTO":
#         """Create a ``StatementRowsDTO`` from an ordered tuple."""
#         (
#             nsd,
#             company_name,
#             quarter,
#             version,
#             grupo,
#             quadro,
#             account,
#             description,
#             value,
#         ) = values
#         return StatementRowsDTO(
#             nsd=int(nsd),
#             company_name=str(company_name) if company_name is not None else None,
#             quarter=str(quarter) if quarter is not None else None,
#             version=str(version) if version is not None else None,
#             grupo=str(grupo),
#             quadro=str(quadro),
#             account=str(account),
#             description=str(description),
#             value=float(value),
# =======
    def from_dict(raw: dict) -> "StatementRowsDTO":
        """Create a ``StatementRowsDTO`` from a raw dictionary."""
        return StatementRowsDTO(
            nsd=int(raw.get("nsd", 0)),
            company_name=raw.get("company_name"),
            quarter=raw.get("quarter"),
            version=raw.get("version"),
            grupo=str(raw.get("grupo", "")),
            quadro=str(raw.get("quadro", "")),
            account=str(raw.get("account", "")),
            description=str(raw.get("description", "")),
            value=float(raw.get("value", 0.0)),
# >>>>>>> 12ae6caf4c160196a7670d81e7ef87d8a80cd61f
        )
