import utils.logging as logging_utils

from infrastructure.repositories.company_repository import SQLiteCompanyRepository
from infrastructure.scrapers.company_b3_scraper import CompanyB3Scraper
from application.services.company_services import CompanyService

from infrastructure.repositories.nsd_repository import SQLiteNSDRepository
from infrastructure.scrapers.nsd_scraper import NsdScraper
from application.services.nsd_service import NsdService

def main_cli():
    """
    Entry point for the FLY CLI application.
    This function initializes the logging, sets up the necessary dependencies for the
    CompanyService (including the repository and scraper), and executes the main
    company synchronization use case. Upon completion, it prints a confirmation message.
    Raises:
        Any exceptions raised by the CompanyService or its dependencies during execution.
    """
    # starts the application logging
    logging_utils.log_message("Start FLY CLI", level="info")

    # === COMPANY ===
    logging_utils.log_message("Start Companies Sync Use Case", level="info")
    company_repository = SQLiteCompanyRepository()
    company_scraper = CompanyB3Scraper()
    company_service = CompanyService(company_repository, company_scraper)
    # Run the service to execute the main use case for Company
    company_service.run()

    # === NSD ===
    logging_utils.log_message("Start NSD Sync Use Case", level="info")
    nsd_repository = SQLiteNSDRepository()
    nsd_scraper = NsdScraper()
    nsd_service = NsdService(nsd_repository, nsd_scraper)
    nsd_service.run()



    print("done")

