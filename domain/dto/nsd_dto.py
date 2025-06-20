# domain/models/nsd_dto.py

from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass(frozen=True)
class NSDDTO:
    nsd: int
    company_name: Optional[str]
    quarter: Optional[str]
    version: Optional[str]
    nsd_type: Optional[str]
    dri: Optional[str]
    auditor: Optional[str]
    responsible_auditor: Optional[str]
    protocol: Optional[str]
    sent_date: Optional[str]
    reason: Optional[str]

    @staticmethod
    def from_dict(raw: dict) -> "NSDDTO":
        """
        Constrói um NSDDTO a partir de um dicionário bruto vindo do scraping.

        Converte valores de datas para string no formato 'YYYY-MM-DD' ou 'YYYY-MM-DD HH:MM:SS',
        caso já estejam como datetime. Não realiza parsing — espera-se que o HTML já tenha
        sido transformado em tipos Python apropriados.
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
            quarter=format_date(raw.get("quarter")),
            version=raw.get("version"),
            nsd_type=raw.get("nsd_type"),
            dri=raw.get("dri"),
            auditor=raw.get("auditor"),
            responsible_auditor=raw.get("responsible_auditor"),
            protocol=raw.get("protocol"),
            sent_date=format_date(raw.get("sent_date")),
            reason=raw.get("reason")
        )
