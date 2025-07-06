"""Port definition for retrieving statement rows."""

from __future__ import annotations

from abc import ABC, abstractmethod

from domain.dto.nsd_dto import NsdDTO
from domain.dto.statement_rows_dto import StatementRowsDTO


class StatementSourcePort(ABC):
    """Port for fetching parsed statement rows."""

    @abstractmethod
    def fetch(self, row: NsdDTO) -> StatementRowsDTO:
        """Return parsed rows for the given NSD."""
        raise NotImplementedError
