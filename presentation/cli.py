from infrastructure.config import Config
from infrastructure.logging import Logger

from infrastructure.repositories import SQLiteCompanyRepository
from infrastructure.scrapers.company_b3_scraper import CompanyB3Scraper
from application.services.company_services import CompanyService

# from infrastructure.repositories.nsd_repository import SQLiteNSDRepository
# from infrastructure.scrapers.nsd_scraper import NsdScraper
# from application.services.nsd_service import NsdService


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

        self.run_company_sync()
        # self.run_nsd_sync()

        print("done")

    def run_company_sync(self):
        """Run the company synchronization workflow."""

        # Log the start of the company synchronization
        self.logger.log("Start Companies Sync Use Case", level="info")

        repo = SQLiteCompanyRepository(config=self.config, logger=self.logger)
        scraper = CompanyB3Scraper(config=self.config, logger=self.logger, data_cleaner=self.data_cleaner)
        service = CompanyService(logger=self.logger, repository=repo, scraper=scraper)

        service.run()

    # def run_nsd_sync(self):
    #     """Run the NSD synchronization workflow."""

    #     # Log the start of the NSD synchronization
    #     self.logger.log("Start NSD Sync Use Case", level="info")

    #     repo = SQLiteNSDRepository(config=self.config)
    #     scraper = NsdScraper(config=self.config)
    #     service = NsdService(repo, scraper)

    #     service.run()
