import utils.logging as logging_utils
from infrastructure.repositories.company_repository import SQLiteCompanyRepository
from infrastructure.scrapers.company_b3_scraper import CompanyB3Scraper
from application.services.company_services import CompanyService

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

    # Create the Company Application Service with injected dependencies
    logging_utils.log_message("Start Companies Sync Use Case", level="info")
    repository = SQLiteCompanyRepository()
    scraper = CompanyB3Scraper()
    service = CompanyService(repository, scraper)

    # Run the service to execute the main use case for Company
    service.run()

    print("done")

