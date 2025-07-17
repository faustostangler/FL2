from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class StatementRowsDTO:
    """Immutable DTO for parsed statement rows."""

    nsd: str
    company_name: Optional[str]
    quarter: Optional[str]
    version: Optional[str]
    grupo: str
    quadro: str
    account: str
    description: str
    value: float

    @staticmethod
    def from_dict(raw: dict) -> "StatementRowsDTO":
        """Create a ``StatementRowsDTO`` from a raw dictionary."""

        nsd_raw = raw.get("nsd", "")
        if nsd_raw is None:
            nsd_raw = ""
        nsd_value = str(nsd_raw)
        if not nsd_value:
            raise ValueError("Invalid NSD value")

        return StatementRowsDTO(
            nsd=nsd_value,
            company_name=raw.get("company_name"),
            quarter=raw.get("quarter"),
            version=raw.get("version"),
            grupo=str(raw.get("grupo", "")),
            quadro=str(raw.get("quadro", "")),
            account=str(raw.get("account", "")),
            description=str(raw.get("description", "")),
            value=float(raw.get("value", 0.0)),
        )
