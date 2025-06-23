# Logging Contract

This document summarizes the expected log messages emitted by the main workflow.

## SyncCompaniesUseCase
- "Start SyncCompaniesUseCase" when the use case is initialized.
- "Get Existing Companies from B3" when fetching the initial list from the API.
- "Start CompanyB3Scraper fetch_all" when iterating over company details.
- "Saved X companies" when a batch is persisted.

All other modules follow the same pattern of emitting a start message and relevant progress logs.
