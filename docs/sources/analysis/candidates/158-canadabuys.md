# CanadaBuys (catalog_id=158)

| Field | Value |
|-------|-------|
| Analysis | TODO_ACCESS |
| Category | H |
| verification_status | UNDER_REVIEW |
| access_mode | open_data_or_portal |
| connector_key | — |

## Official / docs
- Official: https://canadabuys.canada.ca/
- Docs / developer: https://canadabuys.canada.ca/
- Terms / robots notes: Use only authorized APIs/open data; procurement ≠ job postings (ADR-003).

## Access path (for future connector)
- Preferred: open data
- Endpoint candidates (method + URL):
  - CanadaBuys open data exports (https://canadabuys.canada.ca/)
- Auth: None for open data tiers
- Pagination: Dataset slices

## Job list / page structure (if known)
- Content-Type: varies
- Structure: CSV/JSON procurement notices

## Field map sketch → RawJob
| Source | RawJob | Notes |
|--------|--------|-------|
| tender metadata | procurement context | Canada open notices |

## Geo / role fit
- Countries: Canada
- Fit for FMI Demand Compass: reference, FX, taxonomy, procurement context, or import — **not** primary vacancy KPIs unless explicitly jobs.

## Gaps / next step
- Confirm latest API/export URL; OCDS alignment.
