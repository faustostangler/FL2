from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class RawStatementDTO:
    """Immutable DTO representing a scraped statement row."""

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
    def from_dict(raw: dict) -> "RawStatementDTO":
        """Create a ``RawStatementDTO`` from a raw dictionary."""

        nsd_value = raw.get("nsd")

        return RawStatementDTO(
            nsd=str(nsd_value) if nsd_value is not None else "",
            company_name=raw.get("company_name"),
            quarter=raw.get("quarter"),
            version=raw.get("version"),
            grupo=str(raw.get("grupo", "")),
            quadro=str(raw.get("quadro", "")),
            account=str(raw.get("account", "")),
            description=str(raw.get("description", "")),
            value=float(raw.get("value", 0.0)),
        )
