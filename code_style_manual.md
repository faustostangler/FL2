# Code Style Manual

This project adopts a simple style derived from the current implementation.

- One processor class per concern (`EntryCleaner`, `DetailFetcher`, `CompanyMerger`).
- Prefer methods named `run()`, `load()`, `transform()` and `persist()` when composing pipelines.
- Import order follows: standard library, third party, then local modules.
- Use typed dataclasses instead of plain dictionaries for data passed between layers.
- All DTOs are immutable (`@dataclass(frozen=True)`).
- Write docstrings in Google style.
- Compose classes via dependency injection (e.g. `Logger`, `DataCleaner`, `Scraper`).
- Tests are written with `pytest` and placed under `tests/` using the `test_*.py` convention.
