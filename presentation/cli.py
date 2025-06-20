import utils.logging as logging_utils
from infrastructure.repositories.company_repository import SQLiteCompanyRepository
from infrastructure.scrapers.company_scraper import CompanyScraper
from application.services.company_services import CompanyService

def main_cli():
    logging_utils.log_message("Start FLY CLI", level="info")

    # Create the Company Application Service with injected dependencies
    logging_utils.log_message("Start Companies Sync Use Case", level="info")
    repository = SQLiteCompanyRepository()
    scraper = CompanyScraper()
    service = CompanyService(repository, scraper)

    service.run()

    print("done")

