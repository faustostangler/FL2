# domain/models/nsd_dto.py

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class NSDDTO:
    nsd: int
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
    def from_dict(raw: dict) -> "NSDDTO":
        """Build an ``NSDDTO`` from scraped raw data.

        Date values are converted to ``YYYY-MM-DD`` or ``YYYY-MM-DD HH:MM:SS`` strings
        if already ``datetime`` objects. Parsing is not performed; the HTML is expected
        to be preprocessed into proper Python types.
        """

        def format_date(val: Optional[datetime]) -> Optional[str]:
            if isinstance(val, datetime):
                return val.strftime("%Y-%m-%d %H:%M:%S")
            if isinstance(val, str):
                return val.strip()
            return None

        return NSDDTO(
            nsd=int(raw.get("nsd", 0)),
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
