"""Command line interface that wires together the application services."""

from application import CompanyMapper
from application.services.company_service import CompanyService
from application.services.nsd_service import NsdService
from application.services.statement_fetch_service import StatementFetchService
from application.services.statement_parse_service import StatementParseService
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
    SqlAlchemyCompanyRepository,
    SqlAlchemyNsdRepository,
    SqlAlchemyStatementRepository,
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

        self.logger.log(f"Start Class {self.__class__.__name__}", level="info")

    def run(self):
        """Execute the main CLI tasks sequentially."""
        # Start the company synchronization workflow.
        self.logger.log("Call Method CompanyService inside Controller", level="info")
        self._company_service()
        self.logger.log("End Method inside Controller", level="info")

        self.logger.log("Call Method NsdService inside Controller", level="info")
        self._nsd_service()
        self.logger.log("End Method NsdService inside Controller", level="info")

        self.logger.log("Call Method StatementService inside Controller", level="info")
        self._statement_service()
        self.logger.log("End Method StatementService inside Controller", level="info")

    def _company_service(self):
        """Build and run the company synchronization workflow."""
        # Mapper transforms scraped data into DTOs.
        self.logger.log("Start Class CompanyMapper", level="info")
        mapper = CompanyMapper(self.data_cleaner)
        self.logger.log("Finish Class CompanyMapper", level="info")

        # Collector gathers metrics for the worker pool.
        self.logger.log("Start Class MetricsCollector", level="info")
        collector = MetricsCollector()
        self.logger.log("Finish Class MetricsCollector", level="info")

        # Worker pool executes scraping tasks concurrently.
        self.logger.log("Start Class WorkerPool", level="info")
        worker_pool_executor = WorkerPool(self.config, metrics_collector=collector)
        self.logger.log("Finish Class WorkerPool", level="info")

        # Create repository for persistent storage.
        self.logger.log("Start Class SqlAlchemyCompanyRepository", level="info")
        company_repo = SqlAlchemyCompanyRepository(
            config=self.config, logger=self.logger
        )
        self.logger.log("Finish Class SqlAlchemyCompanyRepository", level="info")

        # Create Scraper
        self.logger.log("Start Class CompanyExchangeScraper", level="info")
        company_scraper = CompanyExchangeScraper(
            config=self.config,
            logger=self.logger,
            data_cleaner=self.data_cleaner,
            mapper=mapper,
            worker_pool_executor=worker_pool_executor,
            metrics_collector=collector,
        )
        self.logger.log("Finish Class CompanyExchangeScraper", level="info")

        # Service coordinates the synchronization UseCase.
        self.logger.log("Start Class CompanyService", level="info")
        company_service = CompanyService(
            config=self.config,
            logger=self.logger,
            repository=company_repo,
            scraper=company_scraper,
        )

        # Trigger the actual company synchronization process.
        self.logger.log("Call Method company_service run", level="info")
        company_service.run()
        self.logger.log("Finish Method company_service run", level="info")

        self.logger.log("Finish Class CompanyService", level="info")

    def _nsd_service(self):
        """Build and run the NSD synchronization workflow."""
        # Create repository for persistent storage.
        self.logger.log("Start Class SqlAlchemyNsdRepository", level="info")
        nsd_repo = SqlAlchemyNsdRepository(config=self.config, logger=self.logger)
        self.logger.log("Finish Class SqlAlchemyNsdRepository", level="info")

        # Collector gathers metrics for the worker pool.
        self.logger.log("Start Class MetricsCollector", level="info")
        collector = MetricsCollector()
        self.logger.log("Finish Class MetricsCollector", level="info")

        # Worker pool executes scraping tasks concurrently.
        self.logger.log("Start Class WorkerPool", level="info")
        worker_pool_executor = WorkerPool(self.config, metrics_collector=collector)
        self.logger.log("Finish Class WorkerPool", level="info")

        # Assemble the scraper with all its collaborators.
        self.logger.log("Start Class NsdScraper", level="info")
        nsd_scraper = NsdScraper(
            config=self.config,
            logger=self.logger,
            data_cleaner=self.data_cleaner,
            worker_pool_executor=worker_pool_executor,
            metrics_collector=collector,
            repository=nsd_repo,
        )
        self.logger.log("Finish Class NsdScraper", level="info")

        self.logger.log("Start Class NsdService", level="info")
        nsd_service = NsdService(
            logger=self.logger,
            repository=nsd_repo,
            scraper=nsd_scraper,
        )

        self.logger.log("Call Method nsd_service run", level="info")
        nsd_service.run()
        self.logger.log("End Method nsd_service run", level="info")

        self.logger.log("Finish Class NsdService", level="info")

    def _statement_service(self) -> None:
        """Build and run the statement processing workflow."""
        self.logger.log("Start Class SqlAlchemyCompanyRepository", level="info")
        company_repo = SqlAlchemyCompanyRepository(
            config=self.config, logger=self.logger
        )
        self.logger.log("Finish Class SqlAlchemyCompanyRepository", level="info")

        self.logger.log("Start Class SqlAlchemyNsdRepository", level="info")
        nsd_repo = SqlAlchemyNsdRepository(config=self.config, logger=self.logger)
        self.logger.log("Finish Class SqlAlchemyNsdRepository", level="info")

        self.logger.log("Start Class SqlAlchemyStatementRepository", level="info")
        statement_repo = SqlAlchemyStatementRepository(
            config=self.config, logger=self.logger
        )
        self.logger.log("Finish Class SqlAlchemyStatementRepository", level="info")

        self.logger.log("Start Class RequestsStatementSourceAdapter", level="info")
        source = RequestsStatementSourceAdapter(
            config=self.config, logger=self.logger, data_cleaner=self.data_cleaner
        )
        self.logger.log("Finish Class RequestsStatementSourceAdapter", level="info")

        self.logger.log("Start Class FetchStatementsUseCase", level="info")
        fetch_uc = FetchStatementsUseCase(
            logger=self.logger,
            source=source,
            config=self.config,
            max_workers=self.config.global_settings.max_workers,
        )
        self.logger.log("Finish Class FetchStatementsUseCase", level="info")

        self.logger.log("Start Class ParseAndClassifyStatementsUseCase", level="info")
        parse_uc = ParseAndClassifyStatementsUseCase(logger=self.logger)
        self.logger.log("Finish Class ParseAndClassifyStatementsUseCase", level="info")

        self.logger.log("Start Class PersistStatementsUseCase", level="info")
        persist_uc = PersistStatementsUseCase(
            logger=self.logger, repository=statement_repo
        )
        self.logger.log("Finish Class PersistStatementsUseCase", level="info")

        self.logger.log("Start Class StatementFetchService", level="info")
        statements_fetch_service = StatementFetchService(
            logger=self.logger,
            fetch_usecase=fetch_uc,
            company_repo=company_repo,
            nsd_repo=nsd_repo,
            statement_repo=statement_repo,
            config=self.config,
            max_workers=self.config.global_settings.max_workers,
        )
        self.logger.log("Call Method statements_fetch_service run", level="info")
        raw_rows = statements_fetch_service.run()
        self.logger.log("End Method statements_fetch_service run", level="info")

        self.logger.log("Finish Class StatementFetchService", level="info")

        self.logger.log("Start Class StatementParseService", level="info")
        parse_service = StatementParseService(
            logger=self.logger,
            parse_usecase=parse_uc,
            persist_usecase=persist_uc,
            config=self.config,
            max_workers=self.config.global_settings.max_workers,
        )

        self.logger.log("Call Method parse_service run", level="info")
        parse_service.run(raw_rows)
        self.logger.log("End Method parse_service run", level="info")

        self.logger.log("Finish Class StatementParseService", level="info")
