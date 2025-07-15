# Structural Model - FLY Project

This document summarizes the class relationships and dependencies in the FLY project according to the Hexagonal Architecture.

## Presentation Layer
- **CLI (`presentation/cli.py`)** – builds the object graph and triggers services.

## Application Layer
- **Services**
  - `CompanyService` – orchestrates company synchronization using `SyncCompaniesUseCase`.
  - `NsdService` – orchestrates NSD synchronization via `SyncNSDUseCase`.
  - `StatementFetchService` – fetches raw statement pages with `FetchStatementsUseCase`.
  - `StatementParseService` – parses and persists rows using `ParseAndClassifyStatementsUseCase` and a `WorkerPool`.
  - `NsdPredictionService` – computes missing NSD numbers from repository data.
- **Use Cases**
  - `SyncCompaniesUseCase` – fetches companies and saves them to the repository.
  - `SyncNSDUseCase` – downloads NSD documents and persists them.
  - `FetchStatementsUseCase` – retrieves raw statement rows concurrently.
  - `ParseAndClassifyStatementsUseCase` – converts rows to `StatementDTO` and persists them.
- **Mappers**
  - `CompanyMapper` – merges listing and detail DTOs using a `DataCleaner`.

Dependencies are injected through constructors and point inward to domain ports and DTOs.

## Domain Layer
- **DTOs** (`domain/dto`)
  - `CompanyDTO`, `CompanyRawDTO`, `CompanyListingDTO`, `CompanyDetailDTO`
  - `NsdDTO`
  - `StatementDTO`, `StatementRowsDTO`
  - `ExecutionResultDTO`, `PageResultDTO`, `MetricsDTO`, `SyncCompaniesResultDTO`, `WorkerTaskDTO`
- **Ports** (`domain/ports`)
  - Repository ports: `SqlAlchemyCompanyRepositoryPort`, `NSDRepositoryPort`, `RawStatementRepositoryPort`, `ParsedStatementRepositoryPort`.
  - Source ports: `CompanySourcePort`, `NSDSourcePort`, `RawStatementSourcePort`.
  - `LoggerPort`, `WorkerPoolPort`, `MetricsCollectorPort`, `DataCleanerPort`.
- **Utilities**
  - `statement_processing.classify_section` – maps account names to statement sections.

The domain contains no infrastructure references and consists only of dataclasses and protocols.

## Infrastructure Layer
- **Repositories** (`infrastructure/repositories`)
  - `SqlAlchemyCompanyRepository`, `SqlAlchemyNSDRepository`, `SqlAlchemyRawStatementRepository`, `SqlAlchemyParsedStatementRepository` – implement respective repository ports and manage database persistence using SQLAlchemy.
  - `SqlAlchemyRepositoryBase` – shared connection logic used by concrete repositories.
- **Scrapers & Adapters** (`infrastructure/scrapers`)
  - `CompanyExchangeScraper` – implements `CompanySourcePort` using `FetchUtils`, `DataCleaner`, and several processor classes (`EntryCleaner`, `DetailFetcher`, `CompanyMerger`, `CompanyDetailProcessor`).
  - `NsdScraper` – implements `NSDSourcePort` and fetches sequential documents.
  - `StatementsSourceAdapter` – implements `RawStatementSourcePort` for statement pages.
- **Helpers** (`infrastructure/helpers`)
  - `FetchUtils` – HTTP fetching with retry logic.
  - `SaveStrategy` – buffers DTOs before persistence.
  - `WorkerPool` – thin wrapper over `ThreadPoolExecutor`.
  - `MetricsCollector`, `ByteFormatter`, `DataCleaner`, `TimeUtils`.
- **Logging** (`infrastructure/logging`)
  - `Logger` – emits structured logs.
  - `ProgressFormatter`, `ContextTracker`.
- **Configuration** (`infrastructure/config`)
  - `Config` – aggregates all configuration sections such as exchange endpoints and global settings.

Infrastructure classes depend only on interfaces defined in the domain/application layers.

## Example Constructor Signatures
```python
class CompanyService:
    def __init__(
        self,
        config: Config,
        logger: LoggerPort,
        repository: SqlAlchemyCompanyRepositoryPort,
        scraper: CompanySourcePort,
    ) -> None:
        ...
```
```python
class SqlAlchemyCompanyRepository(SqlAlchemyCompanyRepositoryPort):
```

```python
class SqlAlchemyCompanyRepositoryPort(SqlAlchemyRepositoryBasePort[CompanyDTO, str]):
```

```python
class SqlAlchemyRepositoryBasePort(ABC, Generic[T, K]):
```
e também 

```python
class CompanyExchangeScraper(CompanySourcePort):
```

```python
class CompanySourcePort(BaseSourcePort[CompanyRawDTO]):
```

```python
class BaseSourcePort(ABC, Generic[T]):
```

Dependencies always point inward (scrapers depend on ports and helpers, services depend on use cases and ports).

## Layer Rules Verification
- Domain modules import only other domain modules.
- Application modules depend on domain DTOs and ports, not on infrastructure.
- Infrastructure implementations import domain ports to satisfy interfaces but never import application logic.
- Presentation layer imports services from application to start workflows.

This structure enables testing and swapping implementations while keeping business rules isolated in the domain.