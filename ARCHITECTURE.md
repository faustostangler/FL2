# Architecture

FLY follows the principles of Hexagonal Architecture. The code is organised in four layers:

```
Presentation ↔ Application ↔ Domain ↔ Infrastructure
```

- **Presentation** – The CLI controller in `presentation/cli.py` starts the application.
- **Application** – Services and use cases orchestrate domain logic. Examples are `CompanyService` and `SyncCompaniesUseCase`.
- **Domain** – Pure dataclasses and ports defining contracts (`domain/dto`, `domain/ports`).
- **Infrastructure** – Concrete adapters such as scrapers and repositories.

Dependencies flow inward only: presentation depends on application, which depends on domain. Infrastructure implements ports from the domain but does not import from application.

## Key Concepts

- **Controller** – Triggers execution (CLI).
- **Service** – Coordinates use cases and domain objects.
- **UseCase** – Encapsulates a single business scenario, e.g. `SyncCompaniesUseCase`.
- **DTO** – Immutable data container passed across layers. All DTOs live in `domain/dto` and use `@dataclass(frozen=True)`.
- **Port** – Interface defined in `domain/ports` (e.g., `CompanyRepositoryPort`).
- **Repository** – Infrastructure implementation of a port using SQLAlchemy.
- **Entity** – ORM model mapping a table; converts to/from DTO (see `CompanyModel`).

Adapters and helper utilities are injected through constructors so that each component remains testable. `BaseProcessor` is used by the scrapers to compose small processing steps.

Each feature is expressed as a use case class. Services build the use case, inject repositories or scrapers, and expose a `run()` method.
