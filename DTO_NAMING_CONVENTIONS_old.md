# DTO Naming Conventions

This document defines the standard terminology for the various DTOs used across services.

- **`<Entity>ListingDTO`** – Data loaded from the listing endpoint (base information).
- **`<Entity>DetailDTO`** – Information returned by the detail endpoint for a single entity.
- **`<Entity>RawDTO`** – Temporary merge of listing + detail data, used only inside infrastructure to prepare the final object.
- **`<Entity>DTO`** – Immutable domain object created from dicts or a Raw DTO. This is the only DTO propagated to application and domain layers.

### Flow

adapter → `ListingDTO`/`DetailDTO` → `RawDTO` → `EntityDTO` → model/repository

The `RawDTO` should remain an implementation detail. If convenient, the domain `from_dict()` helper may create and discard a `RawDTO` internally, avoiding propagation of intermediate types outside the infrastructure layer.
