"""Command line interface that wires together the application services."""

from application import CompanyMapper
from application.services.company_service import CompanyService
from application.services.nsd_service import NsdService
from application.services.statement_fetch_service import StatementFetchService
from application.services.statement_parse_service import StatementParseService
from application.usecases import (
    FetchStatementsUseCase,
    ParseAndClassifyStatementsUseCase,
)
from domain.ports import LoggerPort
from infrastructure.config import Config
from infrastructure.helpers import WorkerPool
from infrastructure.helpers.metrics_collector import MetricsCollector
from infrastructure.repositories import (
    SqlAlchemyCompanyRepository,
    SqlAlchemyNsdRepository,
    SqlAlchemyStatementRepository,
    SqlAlchemyStatementRowsRepository,
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

        self.logger.log(f"Load Class {self.__class__.__name__}", level="info")

    def run(self):
        """Execute the main CLI tasks sequentially."""
        self.logger.log("Run  Method controller.run()", level="info")

        # Start the company synchronization workflow.
        self.logger.log("Call Method controller.run()._company_service()", level="info")
        self._company_service()
        self.logger.log("End  Method controller.run()._company_service()", level="info")

        self.logger.log("Call Method controller.run()._nsd_service()", level="info")
        self._nsd_service()
        self.logger.log("End  Method controller.run()._nsd_service()", level="info")

        self.logger.log(
            "Call Method controller.run()._statement_service()", level="info"
        )
        self._statement_service()
        self.logger.log(
            "End  Method controller.run()._statement_service()", level="info"
        )

        self.logger.log("End  Method controller.run()", level="info")

    def _company_service(self):
        """Build and run the company synchronization workflow."""

        self.logger.log("Run  Method controller.run()._company_service()", level="info")

        # Mapper transforms scraped data into DTOs.
        self.logger.log("Instantiate mapper", level="info")
        mapper = CompanyMapper(self.data_cleaner)
        self.logger.log("End Instance mapper", level="info")

        # Collector gathers metrics for the worker pool.
        self.logger.log("Instantiate collector", level="info")
        collector = MetricsCollector()
        self.logger.log("End Instance collector", level="info")

        # Worker pool executes scraping tasks concurrently.
        self.logger.log("Instantiate worker_pool_executor", level="info")
        worker_pool_executor = WorkerPool(self.config, metrics_collector=collector)
        self.logger.log("End Instance worker_pool_executor", level="info")

        # Create repository for persistent storage.
        self.logger.log("Instantiate company_repo", level="info")
        company_repo = SqlAlchemyCompanyRepository(
            config=self.config, logger=self.logger
        )
        self.logger.log("End Instance company_repo", level="info")

        # Create Scraper
        self.logger.log(
            "Instantiate company_scraper (mapper, worker_pool_executor, collector)",
            level="info",
        )
        company_scraper = CompanyExchangeScraper(
            config=self.config,
            logger=self.logger,
            data_cleaner=self.data_cleaner,
            mapper=mapper,
            worker_pool_executor=worker_pool_executor,
            metrics_collector=collector,
        )
        self.logger.log(
            "End Instance company_scraper (mapper, worker_pool_executor, collector)",
            level="info",
        )

        # Service coordinates the synchronization UseCase.
        self.logger.log(
            "Instantiate company_service (company_repo, scraper)", level="info"
        )
        company_service = CompanyService(
            config=self.config,
            logger=self.logger,
            repository=company_repo,
            scraper=company_scraper,
        )

        # Trigger the actual company synchronization process.
        self.logger.log(
            "Call Method controller.run().company_service.run()", level="info"
        )
        company_service.run()
        self.logger.log(
            "Finish Method controller.run().company_service.run()", level="info"
        )

        self.logger.log(
            "End Instance company_service (company_repo, scraper)", level="info"
        )

        self.logger.log("End  Method controller.run()", level="info")

    def _nsd_service(self):
        """Build and run the NSD synchronization workflow."""

        self.logger.log("Run  Method controller.run()._nsd_service()", level="info")

        # Create repository for persistent storage.
        self.logger.log("Instantiate nsd_repo", level="info")
        nsd_repo = SqlAlchemyNsdRepository(config=self.config, logger=self.logger)
        self.logger.log("End Instance nsd_repo", level="info")

        # Collector gathers metrics for the worker pool.
        self.logger.log("Instantiate collector", level="info")
        collector = MetricsCollector()
        self.logger.log("End Instance collector", level="info")

        # Worker pool executes scraping tasks concurrently.
        self.logger.log("Instantiate worker_pool_executor", level="info")
        worker_pool_executor = WorkerPool(self.config, metrics_collector=collector)
        self.logger.log("End Instance worker_pool_executor", level="info")

        # Assemble the scraper with all its collaborators.
        self.logger.log(
            "Instantiate nsd_scraper (worker_pool_executor, collector, nsd_repo)",
            level="info",
        )
        nsd_scraper = NsdScraper(
            config=self.config,
            logger=self.logger,
            data_cleaner=self.data_cleaner,
            worker_pool_executor=worker_pool_executor,
            metrics_collector=collector,
            repository=nsd_repo,
        )
        self.logger.log(
            "End Instance nsd_scraper (worker_pool_executor, collector, nsd_repo)",
            level="info",
        )

        self.logger.log("Instantiate nsd_service (nsd_repo, nsd_scraper)", level="info")
        nsd_service = NsdService(
            logger=self.logger,
            repository=nsd_repo,
            scraper=nsd_scraper,
        )

        self.logger.log(
            "Call Method controller.run()._nsd_service().run()", level="info"
        )
        nsd_service.run()
        self.logger.log(
            "End  Method controller.run()._nsd_service().run()", level="info"
        )

        self.logger.log("End Instance nsd_service (nsd_repo, nsd_scraper", level="info")

        self.logger.log("End  Method controller.run()._nsd_service()", level="info")

    def _statement_service(self) -> None:
        """Build and run the statement processing workflow."""

        self.logger.log(
            "Run  Method controller.run()._statement_service()", level="info"
        )

        self.logger.log("Instantiate company_repo", level="info")
        company_repo = SqlAlchemyCompanyRepository(
            config=self.config, logger=self.logger
        )
        self.logger.log("End Instance company_repo", level="info")

        self.logger.log("Instantiate nsd_repo", level="info")
        nsd_repo = SqlAlchemyNsdRepository(config=self.config, logger=self.logger)
        self.logger.log("End Instance nsd_repo", level="info")

        self.logger.log("Instantiate statement_repo", level="info")
        statement_repo = SqlAlchemyStatementRepository(
            config=self.config, logger=self.logger
        )
        self.logger.log("End Instance statement_repo", level="info")

        self.logger.log("Instantiate raw_rows_repo", level="info")
        raw_rows_repo = SqlAlchemyStatementRowsRepository(
            config=self.config,
            logger=self.logger,
        )
        self.logger.log("End Instance raw_rows_repo", level="info")

        self.logger.log("Instantiate source", level="info")
        source = RequestsStatementSourceAdapter(
            config=self.config, logger=self.logger, data_cleaner=self.data_cleaner
        )
        self.logger.log("End Instance source", level="info")

        self.logger.log("Instantiate fetch_uc (source)", level="info")
        fetch_uc = FetchStatementsUseCase(
            logger=self.logger,
            source=source,
            repository=raw_rows_repo,
            config=self.config,
            max_workers=self.config.global_settings.max_workers,
        )
        self.logger.log("End Instance fetch_uc (source)", level="info")

        self.logger.log("Instantiate parse_uc", level="info")
        parse_uc = ParseAndClassifyStatementsUseCase(
            logger=self.logger,
            repository=statement_repo,
            config=self.config,
        )
        self.logger.log("End Instance parse_uc", level="info")

        # UseCase 1: Fetch
        self.logger.log(
            "Instantiate statements_fetch_service (fetch_uc, company_repo, nsd_repo, statement_repo)",
            level="info",
        )
        statements_fetch_service = StatementFetchService(
            logger=self.logger,
            fetch_usecase=fetch_uc,
            company_repo=company_repo,
            nsd_repo=nsd_repo,
            statement_repo=statement_repo,
            config=self.config,
            max_workers=self.config.global_settings.max_workers,
        )
        self.logger.log(
            "Call Method controller.run()._statement_service().statements_fetch_service.run()",
            level="info",
        )
        raw_rows = statements_fetch_service.run()
        self.logger.log(
            "End  Method controller.run()._statement_service().statements_fetch_service.run()",
            level="info",
        )

        self.logger.log(
            "End Instance statements_fetch_service (fetch_uc, company_repo, nsd_repo, statement_repo)",
            level="info",
        )

        # UseCase 2: Parse
        self.logger.log("Instantiate parse_service (parse_uc)", level="info")
        parse_service = StatementParseService(
            logger=self.logger,
            parse_usecase=parse_uc,
            config=self.config,
            max_workers=self.config.global_settings.max_workers,
        )

        self.logger.log(
            "Call Method controller.run()._statement_service().parse_service.run()",
            level="info",
        )
        parse_service.run(raw_rows)
        self.logger.log(
            "End  Method controller.run()._statement_service().parse_service.run(",
            level="info",
        )

        self.logger.log("End Instance parse_service (parse_uc)", level="info")

        self.logger.log(
            "End  Method controller.run()._statement_service()", level="info"
        )
