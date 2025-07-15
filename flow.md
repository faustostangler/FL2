# Fluxo FLY
## === Infrastructure ===
main.py é o composition-root.
Ele cria as dependências Config, Logger e DataCleaner. Depois instancia o driver primário CLIAdapter e as injeta. Então chama o método start_fly().

## === Presentation ===
MetricsCollector é instanciado no construtor de CLIAdapter. WorkerPool (via WorkerPoolPort e o método abstrato run() para multithreading) também é instanciado no construtor de CLIAdapter, com MetricsCollector e WorkerPool injetado. o método run() recebe a injeção de tasks, processor, logger, e opcionalmente, on_result e post_callback. Serão utilizados pelo source na infraestrutura para tarefas multithreading. 

start_fly() é chamado e executa três serviços, em sequência: os métodos _company_service(), _nsd_service() e _statement_service().

## O método _company_service() 
Primeiro instancia Mapper, Repository e Scraper, com a seguintes características. 
Mapper: CompanyMapper
Repository: SqlAlchemyCompanyRepository, que implementa os métodos do contrato CompanyRepositoryPort, o qual herda de BaseRepositoryPort (com os métodos save_all(), get_all(), has_item(), get_by_id() e get_all_primary_keys()), e também do BaseRepository, via BaseRepositoryPort. A implementação respeita o princípio de substituição de Liskov.
Scraper: CompanyExchangeScraper, que implementa o contrato CompanySourcePort, derivado de BaseSourcePort (com o método fetch_all()). Sua construção recebe as dependências criadas CompanyMapper e injetadas WorkerPoolExecutor e MetricsCollector, e também segue o princípio de substituição de Liskov. Além disso, o construtor do CompanyExchangeScraper cria instâncias de EntryCleaner e DetailFetcher (e seu método fetch_detail()), que vão ser injetados na instanciação de CompanyDetailProcessor. O CompanyDetailProcessor contém o método process_entry, que vai realizar a implantação concreta do código. 

Então o método _company_service() instancia o serviço CompanyService com a injeção do Repository e do Scraper, e chama o método sync_companies()

## === Application ===
O construtor do serviço CompanyService recebe repository e scraper e instancia o SyncCompaniesUseCase com a injeção das dependências recebidas. 

O método sync_companies() do CompanyService chama o método synchronize_companies() do SyncCompaniesUseCase. 

O método synchronize_companies() inicia o pipeline completo de sincronização: 
Primeiro coleta os códigos primários existentes via repository, 
Depois chama scraper.fetch_all() passando os códigos a serem ignorados e o método _save_batch() instanciado aqui. Esse método _save_batch() é responsável por persistir os resultados do método fetch_all() da source para método save_all() do repositório. 

Após a execução, calcula o tempo decorrido e os bytes transferidos, e retorna um SyncCompaniesResultDTO com métricas agregadas da execução.

## === Infrastructure ===
O método fetch_all() do CompanyExchangeScraper é implementado através de uma porta CompanySourcePort via BaseSourcePort, e pela implantação concreta no scraper injetado e executa duas etapas: _fetch_companies_list() e _fetch_companies_details(), com a injeção de _save_batch() em ambos. 

Primeiro chama _fetch_companies_list() do CompanyExchangeScraper, que delega a execução (paralela) ao método run() do WorkerPool (instanciado no CLIAdapter), com a injeção das tasks e do método processor(). Cada vez que o método processor for chamado, vai chamar o método _fetch_page(), que é onde a implementação é executada. Os resultados são acumulados e salvos periodicamente por meio do SaveStrategy instanciado. 
O SaveStrategy apresenta  os métodos handle(), que verifica os critérios para chamar o flush(). O flush() chama o método injetado. E o método finalize() chama o métod flush(). 

Depois chama _fetch_companies_details() do CompanyExchangeScraper, que delega a execução (paralela) ao método run() do WorkerPool (instanciado no CLIAdapter), com a injeção das novas tasks, do novo método processor() e do método handle_batch() do SaveStrategy. Os resultados são acumulados e salvos periodicamente por meio dos métodos handle() e flush() do SaveStrategy. O processor vai chamar o método process_entry() do CompanyDetailProcessor que foi instanciado na construção do CompanyExchangeScraper. O process_entry() chama o método fetch_detatil do DetailFetcher injetado e o método merge_details() do CompanyMerger. 

O método run() do WorkerPool é um módulo de multithreading que permite a execução em múltiplos workers do método enviado (chamado processor nos dois casos). Ele utiliza o recurso de ThreadPoolExecutor para chamar várias tarefas simultâneas. Cada worker executa a tarefa recebida com o método recebido. Após, executa o método injetado como onresult. No caso do _fetch_companies_details(), o onresult é o método handle_batch() que chama o método handle_batch() do SaveStrategy e envia o item recebido. 

O resultado é um ExecutionResultDTO contendo os dados e as métricas do processamento.


## O método _nsd_service()
Repository: SqlAlchemyNsdRepository, que implementa os métodos do contrato NSDRepositoryPort, o qual herda de BaseRepositoryPort (com os métodos save_all(), get_all(), has_item(), get_by_id() e get_all_primary_keys()), e também do BaseRepository, via BaseRepositoryPort. A implementação respeita o princípio de substituição de Liskov.
Scraper: NsdScraper, que implementa o contrato NSDSourcePort, derivado de BaseSourcePort (com o método fetch_all()). Sua construção recebe as dependências criadas FetchUtils e injetadas WorkerPoolExecutor e MetricsCollector, e também segue o princípio de substituição de Liskov. 

Então o método _nsd_service() instancia o serviço NsdService com a injeção do Repository e do Scraper, e chama o método sync_nsd()

## === Application ===
O construtor do serviço NsdService recebe repository e scraper e instancia o SyncNSDUseCase com a injeção das dependências recebidas. 

O método sync_nsd() do NsdService chama o método synchronize_nsd() do SyncNSDUseCase. 

O método synchronize_nsd() inicia o pipeline completo de sincronização: 
Primeiro coleta os códigos primários existentes via repository, 
Depois chama scraper.fetch_all() passando os códigos a serem ignorados e o método _save_batch() instanciado aqui. Esse método _save_batch() é responsável por persistir os resultados do método fetch_all() da source para método save_all() do repositório. 

## === Infrastructure ===
O método fetch_all() do NsdScraper é implementado através de uma porta NSDSourcePort via BaseSourcePort, e pela implantação concreta no scraper injetado e executa uma etapa através do método processor(). Chama o método run() do WorkerPoolExecutor e injeta tasks, processor, que é o método processor() e on_result, que é o método handle_batch() que vai chamar o StrategySave.handle(). O processor 

