"""DTO definitions for normalized NSD (Sequential Document Number, in
Portuguese) data."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class NsdDTO:
    """Structured NSD data extracted from the exchange."""

    nsd: str
    company_name: Optional[str]
    quarter: Optional[datetime]
    version: Optional[str]
    nsd_type: Optional[str]
    dri: Optional[str]
    auditor: Optional[str]
    responsible_auditor: Optional[str]
    protocol: Optional[str]
    sent_date: Optional[datetime]
    reason: Optional[str]

    @staticmethod
    def from_dict(raw: dict) -> "NsdDTO":
        """Build an ``NsdDTO`` from scraped raw data."""
        nsd_value = raw.get("nsd")
        # Map raw keys directly to the immutable dataclass fields
        return NsdDTO(
            nsd=str(nsd_value) if nsd_value is not None else "",
            company_name=raw.get("company_name"),
            quarter=raw.get("quarter"),
            version=raw.get("version"),
            nsd_type=raw.get("nsd_type"),
            dri=raw.get("dri"),
            auditor=raw.get("auditor"),
            responsible_auditor=raw.get("responsible_auditor"),
            protocol=raw.get("protocol"),
            sent_date=raw.get("sent_date"),
            reason=raw.get("reason"),
        )
