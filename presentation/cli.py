"""Command line interface that wires together the application services."""

from dataclasses import asdict

import pandas as pd

from application import CompanyMapper
from application.services.company_service import CompanyService
from application.services.nsd_service import NsdService
from application.services.statement_processing_service import (
    StatementProcessingService,
)
from application.usecases import (
    FetchStatementsUseCase,
    ParseAndClassifyStatementsUseCase,
    PersistStatementsUseCase,
)
from domain.ports import LoggerPort
from infrastructure.config import Config
from infrastructure.helpers import WorkerPool
from infrastructure.helpers.metrics_collector import MetricsCollector
from infrastructure.repositories import (
    SqlAlchemyStatementRepository,
    SQLiteCompanyRepository,
    SQLiteNSDRepository,
)
from infrastructure.scrapers.company_exchange_scraper import CompanyExchangeScraper
from infrastructure.scrapers.nsd_scraper import NsdScraper
from infrastructure.scrapers.statements_source_adapter import (
    RequestsStatementSourceAdapter,
)


class CLIController:
    """Controller that orchestrates FLY via the command line."""

    def __init__(self, config: Config, logger: LoggerPort, data_cleaner):
        """Store dependencies used by the CLI controller.

        Args:
            config: Loaded application configuration.
            logger: LoggerPort used to emit CLI progress messages.
            data_cleaner: Helper used by scrapers to sanitize raw data.
        """
        # Persist the provided configuration for later use.
        self.config = config
        # Keep the logger so other methods can output information.
        self.logger = logger
        # The data cleaner is injected into scrapers.
        self.data_cleaner = data_cleaner

    def run(self):
        """Execute the main CLI tasks sequentially."""
        # Announce the CLI startup for visibility.
        self.logger.log("Start FLY CLI", level="info")

        # Run the company synchronization workflow.
        self._run_company_sync()
        self._run_nsd_sync()
        self._run_statement_sync()

        # Indicate the CLI finished executing.
        self.logger.log("Finish FLY CLI", level="info")

    def _run_company_sync(self):
        """Build and run the company synchronization workflow."""
        # Announce the workflow start.
        self.logger.log("Start Companies Sync Use Case", level="info")

        # Create repository for persistent storage.
        company_repo = SQLiteCompanyRepository(config=self.config, logger=self.logger)
        # Mapper transforms scraped data into DTOs.
        mapper = CompanyMapper(self.data_cleaner)
        # Collector gathers metrics for the worker pool.
        collector = MetricsCollector()
        # Worker pool executes scraping tasks concurrently.
        executor = WorkerPool(self.config, metrics_collector=collector)
        # Assemble the scraper with all its collaborators.
        company_scraper = CompanyExchangeScraper(
            config=self.config,
            logger=self.logger,
            data_cleaner=self.data_cleaner,
            mapper=mapper,
            executor=executor,
            metrics_collector=collector,
        )
        # Service coordinates the synchronization use case.
        company_service = CompanyService(
            config=self.config,
            logger=self.logger,
            repository=company_repo,
            scraper=company_scraper,
        )

        # Trigger the actual company synchronization process.
        company_service.run()

        # Log the end of the workflow
        self.logger.log("Finish Companies Sync Use Case", level="info")

    def _run_nsd_sync(self):
        """Build and run the NSD synchronization workflow."""
        self.logger.log("Start NSD Sync Use Case", level="info")

        # Create repository for persistent storage.
        nsd_repo = SQLiteNSDRepository(config=self.config, logger=self.logger)
        # Collector gathers metrics for the worker pool.
        collector = MetricsCollector()
        # Worker pool executes scraping tasks concurrently.
        executor = WorkerPool(self.config, metrics_collector=collector)
        # Assemble the scraper with all its collaborators.
        nsd_scraper = NsdScraper(
            config=self.config,
            logger=self.logger,
            data_cleaner=self.data_cleaner,
            executor=executor,
            metrics_collector=collector,
            repository=nsd_repo,
        )

        nsd_service = NsdService(
            logger=self.logger,
            repository=nsd_repo,
            scraper=nsd_scraper,
        )

        nsd_service.run()

        self.logger.log("Finish NSD Sync Use Case", level="info")

    def _build_statement_targets(self) -> set[str]:
        """Return NSD identifiers for statements that haven't been
        processed."""
        company_repo = SQLiteCompanyRepository(config=self.config, logger=self.logger)
        nsd_repo = SQLiteNSDRepository(config=self.config, logger=self.logger)
        statement_repo = SqlAlchemyStatementRepository(
            config=self.config,
            logger=self.logger,
        )

        companies = company_repo.get_all()
        nsd_records = nsd_repo.get_all()

        if not companies or not nsd_records:
            return set()

        processed = statement_repo.get_all_primary_keys()
        valid_types = set(self.config.domain.statements_types)
        company_names = {c.company_name for c in companies if c.company_name}

        return {
            str(record.nsd)
            for record in nsd_records
            if (
                record.nsd_type in valid_types
                and record.company_name in company_names
                and str(record.nsd) not in processed
            )
        }

    def _run_statement_sync(self) -> None:
        """Build and run the statement processing workflow."""
        self.logger.log("Start Statement Sync Use Case", level="info")

        repo = SqlAlchemyStatementRepository(config=self.config, logger=self.logger)

        endpoint = (
            f"{self.config.exchange.company_endpoint['financial']}?batch={{batch}}"
        )
        source = RequestsStatementSourceAdapter(
            config=self.config,
            logger=self.logger,
            endpoint=endpoint,
        )

        fetch_uc = FetchStatementsUseCase(logger=self.logger, source=source)
        parse_uc = ParseAndClassifyStatementsUseCase(logger=self.logger)
        persist_uc = PersistStatementsUseCase(logger=self.logger, repository=repo)

        service = StatementProcessingService(
            logger=self.logger,
            fetch_usecase=fetch_uc,
            parse_usecase=parse_uc,
            persist_usecase=persist_uc,
            max_workers=self.config.global_settings.max_workers,
        )

        batch_ids = self._build_statement_targets()

        service.process_all(batch_ids)

        self.logger.log("Finish Statement Sync Use Case", level="info")
