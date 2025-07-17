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
    def from_dict(raw: dict) -> Optional[NsdDTO]:
        """Build an ``NsdDTO`` from scraped raw data."""

        if not raw:
            return None  # <- retorna None se nsd estiver ausente ou inválido

        nsd_raw = raw.get("nsd", "")
        if nsd_raw is not None or str(nsd_raw).isdigit():
            nsd_value = (nsd_raw)
        else:
            nsd_value = ""

        return NsdDTO(
            nsd=nsd_value,
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

    @staticmethod
    def from_raw(raw: NsdDTO) -> NsdDTO:
        """Build an NsdDTO from a NsdRawDTO instance."""
        return NsdDTO(
            nsd=raw.nsd,
            company_name=raw.company_name,
            quarter=raw.quarter,
            version=raw.version,
            nsd_type=raw.nsd_type,
            dri=raw.dri,
            auditor=raw.auditor,
            responsible_auditor=raw.responsible_auditor,
            protocol=raw.protocol,
            sent_date=raw.sent_date,
            reason=raw.reason,
        )
