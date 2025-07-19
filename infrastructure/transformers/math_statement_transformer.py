"""Math adapter implementing quarter adjustment logic."""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Tuple

from application.ports import StatementTransformerPort
from domain.dto.parsed_statement_dto import ParsedStatementDTO
from domain.dto.raw_statement_dto import RawStatementDTO
from infrastructure.config import Config


class MathStatementTransformerAdapter(StatementTransformerPort):
    """Adjust quarterly statement values."""

    def __init__(self, config: Config) -> None:
        self.year_end_prefixes = config.transformers.math_year_end_prefixes
        self.cumulative_prefixes = config.transformers.math_cumulative_prefixes

    def _group_key(self, row: RawStatementDTO) -> Tuple[str, str, str]:
        dt = self._parse(row.quarter)
        year = dt.year if dt else 0
        return row.company_name or "", row.account, str(year)

    def _parse(self, quarter: str | None) -> datetime | None:
        if not quarter:
            return None
        try:
            return datetime.fromisoformat(quarter)
        except ValueError:
            return None

    def transform(self, rows: List[RawStatementDTO]) -> List[ParsedStatementDTO]:
        groups: Dict[
            Tuple[str, str, str], List[Tuple[datetime | None, RawStatementDTO]]
        ] = {}
        for row in rows:
            key = self._group_key(row)
            dt = self._parse(row.quarter)
            groups.setdefault(key, []).append((dt, row))

        result: List[ParsedStatementDTO] = []
        for key, items in groups.items():
            items.sort(key=lambda x: (x[0] or datetime.min))
            account = key[1]
            if account.startswith(self.year_end_prefixes):
                result.extend(self._adjust_year_end(items))
            elif account.startswith(self.cumulative_prefixes):
                result.extend(self._adjust_cumulative(items))
            else:
                result.extend(self._as_parsed(items))
        return result

    def _as_parsed(
        self, items: List[Tuple[datetime | None, RawStatementDTO]]
    ) -> List[ParsedStatementDTO]:
        return [ParsedStatementDTO(**row.__dict__) for _dt, row in items]

    def _adjust_year_end(
        self, items: List[Tuple[datetime | None, RawStatementDTO]]
    ) -> List[ParsedStatementDTO]:
        values: List[ParsedStatementDTO] = []
        cumulative = 0.0
        for dt, row in items:
            if dt and dt.month == 12:
                val = row.value - cumulative
            else:
                val = row.value
                cumulative += row.value
            values.append(
                ParsedStatementDTO(
                    **row.__dict__,
                    value=val,
                )
            )
        return values

    def _adjust_cumulative(
        self, items: List[Tuple[datetime | None, RawStatementDTO]]
    ) -> List[ParsedStatementDTO]:
        values: List[ParsedStatementDTO] = []
        cumulative = 0.0
        for dt, row in items:
            val = row.value - cumulative
            cumulative += row.value
            values.append(
                ParsedStatementDTO(
                    **row.__dict__,
                    value=val,
                )
            )
        return values
