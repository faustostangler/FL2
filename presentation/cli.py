from infrastructure.repositories import SQLiteCompanyRepository
from infrastructure.scrapers.company_b3_scraper import CompanyB3Scraper
from application.services.company_services import CompanyService

from infrastructure.repositories.nsd_repository import SQLiteNSDRepository
from infrastructure.scrapers.nsd_scraper import NsdScraper
from application.services.nsd_service import NsdService


class CLIController:
    """
    Controller responsável por orquestrar a execução da aplicação FLY via CLI.
    Coordena a sincronização de dados da B3, documentos NSD e configura os serviços necessários.
    """

    def __init__(self, config, logger):
        self.config = config
        self.logger = logger

    def run(self):
        self.logger.log("Start FLY CLI", level="info")

        self.run_company_sync()
        # self.run_nsd_sync()

        print("done")

    def run_company_sync(self):
        self.logger.log("Start Companies Sync Use Case", level="info")

        repo = SQLiteCompanyRepository(config=self.config, logger=self.logger)
        scraper = CompanyB3Scraper(config=self.config, logger=self.logger)
        service = CompanyService(logger=self.logger, repository=repo, scraper=scraper)

        service.run()

    # def run_nsd_sync(self):
    #     self.logger.log("Start NSD Sync Use Case", level="info")

    #     repo = SQLiteNSDRepository(config=self.config)
    #     scraper = NsdScraper(config=self.config)
    #     service = NsdService(repo, scraper)

    #     service.run()
