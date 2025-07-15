"""Command line interface that wires together the application services."""

from application import CompanyMapper
from application.services.company_service import CompanyService
from application.services.nsd_service import NsdService
from application.services.statement_fetch_service import StatementFetchService

# from application.services.statement_parse_service import StatementParseService
from domain.ports import LoggerPort
from infrastructure.config import Config
from infrastructure.helpers import WorkerPool
from infrastructure.helpers.metrics_collector import MetricsCollector
from infrastructure.repositories import (
    SqlAlchemyCompanyRepository,
    SqlAlchemyNsdRepository,
    SqlAlchemyParsedStatementRepository,
    SqlAlchemyRawStatementRepository,
)
from infrastructure.scrapers.company_exchange_scraper import CompanyExchangeScraper
from infrastructure.scrapers.nsd_scraper import NsdScraper
from infrastructure.scrapers.statements_source_adapter import (
    RequestsRawStatementSourceAdapter,
)


class CLIAdapter:
    """Controller that orchestrates FLY via the command line interface."""

    def __init__(self, config: Config, logger: LoggerPort, data_cleaner):
        """Initialize the CLI adapter with all required dependencies.

        Args:
            config (Config): Loaded application configuration.
            logger (LoggerPort): Logger used to emit progress messages.
            data_cleaner (Any): Data cleaner utility for sanitizing inputs.
        """
        # Armazena a configuração para uso posterior.
        self.config = config
        # Armazena o logger para emissão de logs durante a execução.
        self.logger = logger
        # Ferramenta de limpeza de dados, usada pelos scrapers.
        self.data_cleaner = data_cleaner

        # Instancia o coletor de métricas para acompanhamento das tarefas.
        # self.logger.log("Instantiate collector", level="info")
        self.collector = MetricsCollector()
        # self.logger.log("End Instance collector", level="info")

        # Instancia o pool de workers que executará tarefas concorrentes.
        # self.logger.log("Instantiate worker_pool_executor", level="info")
        self.worker_pool_executor = WorkerPool(
            self.config,
            metrics_collector=self.collector,
            max_workers=self.config.global_settings.max_workers or 1,
        )
        # self.logger.log("End Instance worker_pool_executor", level="info")

        # self.logger.log(f"Load Class {self.__class__.__name__}", level="info")

    def start_fly(self) -> None:
        """Run the FLY application by executing its main components in sequence."""
        # self.logger.log("Run  Method controller.run()", level="info")

        # Executa o serviço de sincronização de empresas.
        # self.logger.log("Call Method controller.run()._company_service()", level="info")
        self._company_service()
        # self.logger.log("End  Method controller.run()._company_service()", level="info")

        # Executa o serviço de sincronização de NSDs.
        # self.logger.log("Call Method controller.run()._nsd_service()", level="info")
        self._nsd_service()
        # self.logger.log("End  Method controller.run()._nsd_service()", level="info")

        # Executa o serviço de coleta e armazenamento de demonstrativos.
        # self.logger.log("Call Method controller.run()._statement_service()", level="info")
        self._statement_service()
        # self.logger.log("End  Method controller.run()._statement_service()", level="info")

        # self.logger.log("End  Method controller.run()", level="info")

    def _company_service(self) -> None:
        """Assemble and execute the company synchronization flow."""

        # Mapper transforma dados brutos em objetos de domínio.
        # self.logger.log("Instantiate mapper", level="info")
        mapper = CompanyMapper(self.data_cleaner)
        # self.logger.log("End Instance mapper", level="info")

        # Repositório para persistência de empresas.
        # self.logger.log("Instantiate company_repo", level="info")
        company_repo = SqlAlchemyCompanyRepository(config=self.config, logger=self.logger)
        # self.logger.log("End Instance company_repo", level="info")

        # Scraper responsável por obter dados das empresas.
        # self.logger.log("Instantiate company_scraper (mapper, worker_pool_executor, collector)", level="info")
        company_scraper = CompanyExchangeScraper(
            config=self.config,
            logger=self.logger,
            data_cleaner=self.data_cleaner,
            mapper=mapper,
            worker_pool_executor=self.worker_pool_executor,
            metrics_collector=self.collector,
        )
        # self.logger.log("End Instance company_scraper (mapper, worker_pool_executor, collector)", level="info")

        # Serviço que orquestra a sincronização das empresas.
        # self.logger.log("Instantiate company_service (company_repo, scraper)", level="info")
        company_service = CompanyService(
            config=self.config,
            logger=self.logger,
            repository=company_repo,
            scraper=company_scraper,
        )

        # Executa a sincronização.
        # self.logger.log("Call Method controller.start().company_service.sync_companies()", level="info")
        company_service.sync_companies()
        # self.logger.log("Finish Method controller.start().company_service.sync_companies()", level="info")

    def _nsd_service(self) -> None:
        """Assemble and execute the NSD synchronization flow."""

        # Repositório para persistência dos NSDs.
        # self.logger.log("Instantiate nsd_repo", level="info")
        nsd_repo = SqlAlchemyNsdRepository(config=self.config, logger=self.logger)
        # self.logger.log("End Instance nsd_repo", level="info")

        # Scraper que coleta NSDs diretamente das fontes.
        # self.logger.log("Instantiate nsd_scraper (worker_pool_executor, collector, nsd_repo)", level="info")
        nsd_scraper = NsdScraper(
            config=self.config,
            logger=self.logger,
            data_cleaner=self.data_cleaner,
            repository=nsd_repo,
            worker_pool_executor=self.worker_pool_executor,
            metrics_collector=self.collector,
        )
        # self.logger.log("End Instance nsd_scraper (worker_pool_executor, collector, nsd_repo)", level="info")

        # Serviço responsável pela lógica de sincronização dos NSDs.
        # self.logger.log("Instantiate nsd_service (nsd_repo, nsd_scraper)", level="info")
        nsd_service = NsdService(
            logger=self.logger,
            repository=nsd_repo,
            scraper=nsd_scraper,
        )

        # Executa a sincronização.
        # self.logger.log("Call Method controller.start()._nsd_service().sync_nsd()", level="info")
        nsd_service.sync_nsd()
        # self.logger.log("End  Method controller.start()._nsd_service().sync_nsd()", level="info")

    def _statement_service(self) -> None:
        """Assemble and execute the statement retrieval and transformation flow."""

        # Instancia repositórios para acesso a entidades persistidas.
        # self.logger.log("Instantiate company_repo", level="info")
        company_repo = SqlAlchemyCompanyRepository(config=self.config, logger=self.logger)
        # self.logger.log("End Instance company_repo", level="info")

        # self.logger.log("Instantiate nsd_repo", level="info")
        nsd_repo = SqlAlchemyNsdRepository(config=self.config, logger=self.logger)
        # self.logger.log("End Instance nsd_repo", level="info")

        # self.logger.log("Instantiate raw_statement_repo", level="info")
        raw_statement_repo = SqlAlchemyRawStatementRepository(config=self.config, logger=self.logger)
        # self.logger.log("End Instance raw_statement_repo", level="info")

        # self.logger.log("Instantiate parsed_statements_repo", level="info")
        parsed_statements_repo = SqlAlchemyParsedStatementRepository(config=self.config, logger=self.logger)
        # self.logger.log("End Instance parsed_statements_repo", level="info")

        # Scraper para busca dos demonstrativos originais (em HTML/PDF).
        # self.logger.log("Instantiate source", level="info")
        raw_statements_scraper = RequestsRawStatementSourceAdapter(
            config=self.config,
            logger=self.logger,
            data_cleaner=self.data_cleaner,
            metrics_collector=self.collector,
            worker_pool_executor=self.worker_pool_executor,
        )
        # self.logger.log("End Instance source", level="info")

        # Serviço que busca os demonstrativos e salva no banco.
        # self.logger.log("Instantiate statements_fetch_service (...) ", level="info")
        statements_fetch_service = StatementFetchService(
            logger=self.logger,
            source=raw_statements_scraper,
            parsed_statements_repo=parsed_statements_repo,
            company_repo=company_repo,
            nsd_repo=nsd_repo,
            raw_statement_repo=raw_statement_repo,
            config=self.config,
            metrics_collector=self.collector,
            worker_pool_executor=self.worker_pool_executor,
            max_workers=self.config.global_settings.max_workers,
        )

        # Executa a etapa de fetch e coleta os demonstrativos brutos.
        # self.logger.log("Call Method controller.run()._statement_service().statements_fetch_service.run()", level="info")
        raw_rows = statements_fetch_service.fetch_statements()
        self.logger.log(f"total {len(raw_rows)}")
        # self.logger.log("End  Method controller.run()._statement_service().statements_fetch_service.run()", level="info")

        # A próxima etapa de parse está comentada (StatementParseService).
