# DTO Naming Conventions

DTOs standardise data transferred between layers. All DTOs are immutable dataclasses with `frozen=True` and contain no logic.

## Types

- `RawCompanyDTO` – temporary merge of listing and detail data.
- `CompanyDTO` – validated domain representation used by services and repositories.
- `SyncCompaniesResultDTO` – aggregate with metrics returned by the sync use case.

Use the suffix `DTO` for transport objects only. Instantiate them with all required values and avoid setters.
