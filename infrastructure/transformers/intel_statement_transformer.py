"""Financial intelligence adapter that calculates simple ratios."""

from __future__ import annotations

from typing import Dict, List, Tuple

from application.ports import StatementTransformerPort
from domain.dto.parsed_statement_dto import ParsedStatementDTO
from domain.dto.raw_statement_dto import RawStatementDTO


class IntelStatementTransformerAdapter(StatementTransformerPort):
    """Add basic financial ratios to parsed statements."""

    def transform(self, rows: List[RawStatementDTO]) -> List[ParsedStatementDTO]:
        parsed = [
            row
            if isinstance(row, ParsedStatementDTO)
            else ParsedStatementDTO(**row.__dict__)
            for row in rows
        ]

        grouped: Dict[Tuple[str | None, str | None], List[ParsedStatementDTO]] = {}
        for row in parsed:
            key = (row.company_name, row.quarter)
            grouped.setdefault(key, []).append(row)

        results = list(parsed)
        for (company, quarter), items in grouped.items():
            assets = sum(r.value for r in items if r.account.startswith("01"))
            liabilities = sum(r.value for r in items if r.account.startswith("02"))
            ratio = liabilities / assets if assets else 0.0
            base = items[0]
            results.append(
                ParsedStatementDTO(
                    nsd=base.nsd,
                    company_name=company,
                    quarter=quarter,
                    version=base.version,
                    grupo="INDICATORS",
                    quadro="RATIOS",
                    account="11.02",
                    description="Passivos por Ativos",
                    value=ratio,
                )
            )
        return results
