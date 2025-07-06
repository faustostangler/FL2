"""DTO representing statement rows associated with a specific NSD."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

from .nsd_dto import NsdDTO


@dataclass(frozen=True)
class StatementRowsDTO:
    """Container for parsed statement rows associated with an ``NsdDTO``."""

    nsd: NsdDTO
    rows: List[Dict[str, Any]]

    @staticmethod
    def from_tuple(data: Tuple[NsdDTO, List[Dict[str, Any]]]) -> "StatementRowsDTO":
        """Build a ``StatementRowsDTO`` from ``(NsdDTO, rows)`` tuple."""
        nsd, rows = data
        return StatementRowsDTO(nsd=nsd, rows=rows)
