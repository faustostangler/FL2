"""Use case for transforming raw financial statement rows."""

from __future__ import annotations

from typing import List

from application.ports import StatementTransformerPort
from domain.dto.parsed_statement_dto import ParsedStatementDTO
from domain.dto.raw_statement_dto import RawStatementDTO


class TransformStatementsUseCase:
    """Compose math and intel transformers into a single pipeline."""

    def __init__(
        self,
        math_transformer: StatementTransformerPort,
        intel_transformer: StatementTransformerPort,
    ) -> None:
        self.math_transformer = math_transformer
        self.intel_transformer = intel_transformer

    def execute(self, raw_dtos: List[RawStatementDTO]) -> List[ParsedStatementDTO]:
        """Run transformation pipeline for ``raw_dtos``."""
        stage1 = self.math_transformer.transform(raw_dtos)
        stage2 = self.intel_transformer.transform(stage1)  # type: ignore[arg-type]
        return stage2
