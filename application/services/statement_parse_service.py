from __future__ import annotations

from typing import List, Tuple

from application.usecases.parse_and_classify_statements import (
    ParseAndClassifyStatementsUseCase,
)
from domain.dto import NsdDTO, ParsedStatementDTO, WorkerTaskDTO
from domain.dto.raw_statement_dto import RawStatementDTO
from domain.ports import LoggerPort, SqlAlchemyRawStatementRepositoryPort
from infrastructure.config import Config
from infrastructure.helpers import MetricsCollector, WorkerPool


class StatementParseService:
    """Parse raw statement rows and persist cleaned records."""

    def __init__(
        self,
        logger: LoggerPort,
        repository: SqlAlchemyRawStatementRepositoryPort,
        config: Config,
        max_workers: int = 1,
    ) -> None:
        """Store dependencies for the service."""
        self.logger = logger
        self.config = config
        self.max_workers = max_workers

        self.parse_usecase = ParseAndClassifyStatementsUseCase(
            logger=self.logger,
            repository=repository,
            config=self.config,
        )

        # self.logger.log(f"Load Class {self.__class__.__name__}", level="info")

    def _parse_all(
        self, fetched: List[Tuple[NsdDTO, List[RawStatementDTO]]]
    ) -> List[List[ParsedStatementDTO]]:
        collector = MetricsCollector()
        parse_pool = WorkerPool(
            config=self.config,
            metrics_collector=collector,
            max_workers=self.max_workers,
        )

        tasks = list(enumerate(fetched))

        def processor(task: WorkerTaskDTO) -> List[ParsedStatementDTO]:
            _nsd, rows = task.data
            return [self.parse_usecase.parse_and_store_row(r) for r in rows]

        result = parse_pool.run(tasks=tasks, processor=processor, logger=self.logger)
        return result.items

    def parse_statements(
        self, fetched: List[Tuple[NsdDTO, List[RawStatementDTO]]]
    ) -> None:
        """Parse and persist statements from ``fetched`` rows."""
        # self.logger.log("Run  Method statement_parse_service.run()", level="info")

        if not fetched:
            # self.logger.log("No statements to parse", level="info")
            return

        # self.logger.log(
        #     "Call Method statement_parse_service._parse_all()", level="info"
        # )
        self._parse_all(fetched)
        # self.logger.log(
        #     "End  Method statement_parse_service._parse_all()", level="info"
        # )

        self.parse_usecase.finalize()

        # self.logger.log("End  Method statement_parse_service.run()", level="info")
