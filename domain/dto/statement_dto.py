from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class StatementDTO:
    """Immutable representation of a financial statement row."""

    batch_id: str
    account: str
    section: str
    value: float
    company: Optional[str] = None
    period: Optional[str] = None

    @staticmethod
    def from_dict(raw: dict) -> "StatementDTO":
        """Create ``StatementDTO`` from a raw dictionary."""
        return StatementDTO(
            batch_id=str(raw.get("batch_id", "")),
            account=str(raw.get("account", "")),
            section=str(raw.get("section", "")),
            value=float(raw.get("value", 0.0)),
            company=raw.get("company"),
            period=raw.get("period"),
        )
