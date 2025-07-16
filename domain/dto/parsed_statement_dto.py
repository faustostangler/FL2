from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ParsedStatementDTO:
    """Immutable representation of a cleaned statement row."""

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
    def from_dict(raw: dict) -> "ParsedStatementDTO":
        """Create ``ParsedStatementDTO`` from a raw dictionary."""

        try:
            nsd_value = int(raw.get("nsd", 0))
        except (TypeError, ValueError) as exc:
            raise ValueError("Invalid NSD value") from exc

        return ParsedStatementDTO(
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
