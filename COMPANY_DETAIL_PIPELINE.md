# Company Detail Pipeline

The detail pipeline is triggered by `sync_companies.py` via `CompanyService`.

1. `CompanyExchangeScraper.fetch_all()` retrieves a list of companies and for each one:
   - `EntryCleaner` normalizes the listing entry.
   - `DetailFetcher` downloads the detail page and converts it to `CompanyDetailDTO`.
   - `CompanyMerger` merges listing and detail data into `CompanyRawDTO`.
2. The use case converts each `CompanyRawDTO` to `CompanyDTO` and calls the repository.
3. `SqlAlchemyCompanyRepository` persists the data with `insert_or_update` semantics.

All steps emit logs and accumulate metrics. Results are stored in the SQLite tables declared in `infrastructure/models`.
