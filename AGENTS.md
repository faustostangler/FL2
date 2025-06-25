# FLY Agents

This document describes the **main agents** (components/services) in the FLY data pipeline. Each agent follows hexagonal architecture principles, with clearly defined dependencies, injected configuration and logging, and isolation of business logic from infrastructure concerns.

---

## Structure

All agents are implemented as **classes**, not bare functions, and receive their dependencies via constructor injection:

```python
class Agent:
    def __init__(self, config: Config, logger: Logger): ...
    def run(self) -> None: ...
```

They are orchestrated by the CLI controller (`CLIController`), which boots the system in `run.py`.

---

## Core Agents

### CompanyService
- **Layer:** Application  
- **Role:** Coordinates synchronization of company metadata from B3 to the local database.  
- **Dependencies:**  
  - `SyncCompaniesUseCase` (application use case)  
  - `CompanyB3Scraper` (infrastructure scraper implementing `CompanySource`)  
  - `SQLiteCompanyRepository` (persistence adapter implementing `CompanyRepository`)  
- **Workflow:** logger → use case → repository  
- **I/O:** `CompanyDTO`

### SyncCompaniesUseCase
- **Layer:** Application Use Case  
- **Role:** Implements the “fetch-and-save” loop for companies.  
- **Dependencies:**  
  - `SQLiteCompanyRepository`  
  - `CompanyB3Scraper`  
  - `Logger`  
- **Behavior:**  
  1. Load existing CVM codes  
  2. Call `scraper.fetch_all(skip=existing, save_callback=self._save_batch)`  
  3. Convert each raw dict to `CompanyDTO` and `repository.save_all(...)`
- **Note:** This use case coordinates scraping and persistence, but only the repository performs writes. The use case itself has no direct side effects.

### NsdService
- **Layer:** Application  
- **Role:** Coordinates scraping and persistence of NSD (document number) records.  
- **Dependencies:**  
  - `SyncNSDUseCase` (if exists) or direct use of `NsdScraper` (implements `NsdSource`) + `SQLiteNSDRepository` (implements `NSDRepository`)  
- **I/O:** `NSDDTO`

---

## Utilities (Helper Agents)

### FetchUtils
- **Layer:** Infrastructure helper  
- **Role:** HTTP retry logic with randomized headers.  
- **Dependencies:** `Config`, `Logger`  

### TimeUtils
- **Layer:** Infrastructure helper  
- **Role:** Dynamically adjusts `sleep()` based on CPU usage.  
- **Dependencies:** `Config`  

### DataCleaner
- **Layer:** Infrastructure helper  
- **Role:** Normalizes raw scraped values (text, numbers, dates).  
- **Dependencies:** `Config`, `Logger`

---

## Persistence Adapters (ORM Models)

### CompanyModel
- **Location:** `infrastructure/models/company_model.py`  
- **Role:** Maps `CompanyDTO ↔ SQLAlchemy table "tbl_company"`.  
- **Methods:**  
  - `@staticmethod from_dto(dto: CompanyDTO) → CompanyModel`  
  - `to_dto() → CompanyDTO`

### NSDModel
- **Location:** `infrastructure/models/nsd_model.py`  
- **Role:** Maps `NSDDTO ↔ SQLAlchemy table "tbl_nsd"`.  
- **Methods:**  
  - `@staticmethod from_dto(dto: NSDDTO) → NSDModel`  
  - `to_dto() → NSDDTO`

---

## DTOs

All data passed between layers are **immutable dataclasses** in `domain/dto/`:

- `CompanyDTO`  
- `NSDDTO`  

They provide:
- Strict field typing  
- `@staticmethod from_dict(raw: dict) → DTO`  
- No business logic (pure data carriers)

---

## Logging Agent

### Logger
- **Location:** `infrastructure/logging/logger.py`  
- **Role:** Centralized logger based on Python’s `logging` module, with:  
  - Context-aware stack trace (**debug only**)  
  - Progress formatting (percent + ETA)  
  - Injected level control  
- **Usage:** `logger.log("message", level="info", progress={...})`

---

## Deployment & Execution Flow

1. **Entry point:** `run.py`  
2. Instantiate `Config()` and `Logger(config)`  
3. Create `CLIController(config, logger)`  
4. `CLIController.run()` calls:  
   - `CompanyService.run()` → `SyncCompaniesUseCase.execute()`  
   - `NsdService.run()` → `SyncNSDUseCase.execute()`  

All agents rely exclusively on injected dependencies; **no globals**.

---

## Summary Table

| Agent                   | Layer               | Role/Type       | I/O            |
|------------------------|---------------------|----------------|---------------|
| CompanyService         | Application         | Controller     | CompanyDTO    |
| SyncCompaniesUseCase   | Application UseCase | Logic          | CompanyDTO    |
| NsdService             | Application         | Controller     | NSDDTO        |
| FetchUtils             | Infrastructure      | Helper Utility | —             |
| TimeUtils              | Infrastructure      | Helper Utility | —             |
| DataCleaner            | Infrastructure      | Helper Utility | str/float/datetime |
| CompanyModel           | Infrastructure      | ORM Adapter    | CompanyDTO    |
| NSDModel               | Infrastructure      | ORM Adapter    | NSDDTO        |
| Logger                 | Infrastructure      | Logging Agent  | string        |

---
