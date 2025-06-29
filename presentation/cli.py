from application import CompanyMapper
from application.services.company_service import CompanyService
from application.services.nsd_service import NsdService
from infrastructure.config import Config
from infrastructure.helpers import WorkerPool
from infrastructure.helpers.metrics_collector import MetricsCollector
from infrastructure.logging import Logger
from infrastructure.repositories import SQLiteCompanyRepository
from infrastructure.repositories.nsd_repository import SQLiteNSDRepository
from infrastructure.scrapers.company_b3_scraper import CompanyB3Scraper
from infrastructure.scrapers.nsd_scraper import NsdScraper


class CLIController:
    """CLI controller that orchestrates the FLY application execution."""

    def __init__(self, config: Config, logger: Logger, data_cleaner):
        """Initialize the controller with config and logger.

        Args:
            config (Config): Application configuration object.
            logger (Logger): Logger used for CLI messages.
        """
        self.config = config
        self.logger = logger
        self.data_cleaner = data_cleaner

    def run(self):
        """Execute the main CLI tasks."""

        # Log the start of the CLI application
        self.logger.log("Start FLY CLI", level="info")

        # self.logger.log("Skip Companies", level="warning")
        self.run_company_sync()
        self.run_nsd_sync()

    def run_company_sync(self):
        """Run the company synchronization workflow."""

        # Log the start of the company synchronization
        self.logger.log("Start Companies Sync Use Case", level="info")

        company_repo = SQLiteCompanyRepository(config=self.config, logger=self.logger)
        mapper = CompanyMapper(self.data_cleaner)
        collector = MetricsCollector()
        executor = WorkerPool(self.config, metrics_collector=collector)
        company_scraper = CompanyB3Scraper(
            config=self.config,
            logger=self.logger,
            data_cleaner=self.data_cleaner,
            mapper=mapper,
            executor=executor,
            metrics_collector=collector,
        )
        company_service = CompanyService(
            config=self.config,
            logger=self.logger,
            repository=company_repo,
            scraper=company_scraper,
        )

        company_service.run()

    def run_nsd_sync(self):
        """Run the NSD synchronization workflow."""
        # Log the start of the NSD synchronization
        self.logger.log("Start NSD Sync Use Case", level="info")

        nsd_repo = SQLiteNSDRepository(config=self.config, logger=self.logger)
        collector = MetricsCollector()
        nsd_scraper = NsdScraper(
            config=self.config,
            logger=self.logger,
            data_cleaner=self.data_cleaner,
            metrics_collector=collector,
        )
        nsd_service = NsdService(
            logger=self.logger, repository=nsd_repo, scraper=nsd_scraper
        )

        nsd_service.run()
