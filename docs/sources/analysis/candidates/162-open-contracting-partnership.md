# Open Contracting Partnership (catalog_id=162)

| Field | Value |
|-------|-------|
| Analysis | DOCUMENTED |
| Category | H |
| verification_status | UNDER_REVIEW |
| access_mode | open_data_or_portal |
| connector_key | — |

## Official / docs
- Official: https://www.open-contracting.org/
- Docs / developer: https://www.open-contracting.org/
- Terms / robots notes: Use only authorized APIs/open data; procurement ≠ job postings (ADR-003).

## Access path (for future connector)
- Preferred: registry / guidance
- Endpoint candidates (method + URL):
  - OCP data registry links to publisher endpoints (https://data.open-contracting.org/en/publication/)
- Auth: N/A
- Pagination: N/A

## Job list / page structure (if known)
- Content-Type: varies
- Structure: Links to publisher OCDS feeds

## Field map sketch → RawJob
| Source | RawJob | Notes |
|--------|--------|-------|
| N/A — discovery meta |

## Geo / role fit
- Countries: Global
- Fit for FMI Demand Compass: reference, FX, taxonomy, procurement context, or import — **not** primary vacancy KPIs unless explicitly jobs.

## Gaps / next step
- Use to locate national OCDS endpoints; not direct ingest.
