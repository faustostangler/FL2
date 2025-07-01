"""Command line interface that wires together the application services."""

from application import CompanyMapper
from application.services.company_service import CompanyService
from infrastructure.config import Config
from infrastructure.helpers import WorkerPool
from infrastructure.helpers.metrics_collector import MetricsCollector
from infrastructure.logging import Logger
from infrastructure.repositories import SQLiteCompanyRepository
from infrastructure.scrapers.company_exchange_scraper import CompanyExchangeScraper


class CLIController:
    """Controller that orchestrates FLY via the command line."""

    def __init__(self, config: Config, logger: Logger, data_cleaner):
        """Store dependencies used by the CLI controller.

        Args:
            config: Loaded application configuration.
            logger: Logger used to emit CLI progress messages.
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
        self.run_company_sync()
        self.run_nsd_sync()

        # Indicate the CLI finished executing.
        self.logger.log("Finish FLY CLI", level="info")

    def run_company_sync(self):
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
    def run_nsd_sync(self):
        """Build and run the NSD synchronization workflow."""

        # Announce the workflow start.
        self.logger.log("Start NSD Sync Use Case", level="info")

        # # Set up repository where NSD data will be persisted.
        # nsd_repo = SQLiteNSDRepository(config=self.config, logger=self.logger)
        # # Collect metrics for the scraping tasks.
        # collector = MetricsCollector()
        # # Scraper fetches data from the NSD site.
        # nsd_scraper = NsdScraper(
        #     config=self.config,
        #     logger=self.logger,
        #     data_cleaner=self.data_cleaner,
        #     metrics_collector=collector,
        # )
        # # Service coordinates NSD synchronization.
        # nsd_service = NsdService(
        #     logger=self.logger,
        #     repository=nsd_repo,
        #     scraper=nsd_scraper,
        # )

        # # Trigger the actual NSD synchronization process.
        # nsd_service.run()
