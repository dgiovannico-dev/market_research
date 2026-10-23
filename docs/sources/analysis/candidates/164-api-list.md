# API List (catalog_id=164)

| Field | Value |
|-------|-------|
| Analysis | DOCUMENTED |
| Category | I |
| verification_status | VALIDATED |
| access_mode | directory |
| connector_key | — |

## Official / docs
- Official: https://apilist.fun/
- Docs / developer: https://apilist.fun/
- Terms / robots notes: Use only authorized APIs/open data; procurement ≠ job postings (ADR-003).

## Access path (for future connector)
- Preferred: directory website
- Endpoint candidates (method + URL):
  - https://apilist.fun/ — browsable API index
- Auth: N/A
- Pagination: Site search

## Job list / page structure (if known)
- Content-Type: varies
- Structure: HTML catalog

## Field map sketch → RawJob
| Source | RawJob | Notes |
|--------|--------|-------|
| N/A |

## Geo / role fit
- Countries: Global
- Fit for FMI Demand Compass: reference, FX, taxonomy, procurement context, or import — **not** primary vacancy KPIs unless explicitly jobs.

## Gaps / next step
- Discovery only; verify licensing per API.
