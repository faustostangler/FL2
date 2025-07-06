from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass(frozen=True)
class StatementRowsDTO:
    """Immutable DTO for parsed statement rows."""

    account: str
    description: str
    value: float
    grupo: str
    quadro: str
    company_name: Optional[str]
    nsd: int
    quarter: Optional[str]
    version: Optional[str]

    @staticmethod
    def from_tuple(values: Tuple) -> "StatementRowsDTO":
        """Create a ``StatementRowsDTO`` from an ordered tuple."""
        keys = [
            "account",
            "description",
            "value",
            "grupo",
            "quadro",
            "company_name",
            "nsd",
            "quarter",
            "version",
        ]

        mapping = dict(zip(keys, values))

        mapping["account"] = str(mapping.get("account"))
        mapping["description"] = str(mapping.get("description"))
        mapping["value"] = float(mapping.get("value"))
        mapping["grupo"] = str(mapping.get("grupo"))
        mapping["quadro"] = str(mapping.get("quadro"))
        company_name = mapping.get("company_name")
        mapping["company_name"] = (
            str(company_name) if company_name is not None else None
        )
        mapping["nsd"] = int(mapping.get("nsd"))
        quarter = mapping.get("quarter")
        mapping["quarter"] = str(quarter) if quarter is not None else None
        version = mapping.get("version")
        mapping["version"] = str(version) if version is not None else None

        return StatementRowsDTO(**mapping)
