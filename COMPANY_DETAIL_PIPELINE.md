# Company Detail Processing Pipeline

The company detail workflow uses a small pipeline of processors to keep each step focused on a single responsibility:

1. **EntryCleaner** – normalizes raw listing data and converts it to `CompanyListingDTO`.
2. **DetailFetcher** – retrieves the detail page for a company and converts it to `CompanyDetailDTO` while recording network metrics.
3. **CompanyMerger** – merges the listing and detail DTOs into a single `CompanyRawDTO`.
4. **CompanyDetailProcessor** – orchestrates the three steps above and returns the final DTO.

This pipeline is instantiated in `CompanyB3Scraper` and used inside `_fetch_companies_details`. Each processor is a class with its dependencies injected via the constructor, following the project’s hexagonal architecture guidelines.
