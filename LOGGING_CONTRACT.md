# Logging Contract

This document summarizes the expected log messages emitted by the main workflow.

## SyncCompaniesUseCase
- "Start SyncCompaniesUseCase" when the use case begins.
- "Get Existing Companies from B3" when loading the initial list.
- "Start CompanyB3Scraper fetch_all" when iterating over company details.
- "Saved X companies" after each persistence batch.

Example:
```json
{"level": "info", "message": "Saved 50 companies", "progress": {"current": 50, "total": 200}, "extra": {"batch": 1}}
```

## Responsibilities
Each processing agent must emit logs upon start, at meaningful checkpoints, and after major operations (e.g., save, skip, error). Scrapers and UseCases are required to log these events. Mappers and helper utilities may log as needed but are optional.
