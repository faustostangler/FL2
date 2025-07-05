"""DTO for raw statement rows returned by the scraper."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class RawStatementDTO:
    """Raw statement row scraped from the exchange."""

    account: str
    description: str
    value: float
    grupo: str
    quadro: str
    company_name: str
    nsd: int
    quarter: Optional[str]
    version: str

    @staticmethod
    def from_dict(raw: dict) -> "RawStatementDTO":
        """Create ``RawStatementDTO`` from a raw dictionary."""
        return RawStatementDTO(
            account=str(raw.get("account", "")),
            description=str(raw.get("description", "")),
            value=float(raw.get("value", 0.0)),
            grupo=str(raw.get("grupo", "")),
            quadro=str(raw.get("quadro", "")),
            company_name=str(raw.get("company_name", "")),
            nsd=int(raw.get("nsd", 0)),
            quarter=raw.get("quarter"),
            version=str(raw.get("version", "")),
        )
