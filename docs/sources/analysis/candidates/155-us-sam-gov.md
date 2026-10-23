# US SAM.gov (catalog_id=155)

| Field | Value |
|-------|-------|
| Analysis | TODO_ACCESS |
| Category | H |
| verification_status | UNDER_REVIEW |
| access_mode | open_data_or_portal |
| connector_key | — |

## Official / docs
- Official: https://sam.gov/
- Docs / developer: https://sam.gov/
- Terms / robots notes: Use only authorized APIs/open data; procurement ≠ job postings (ADR-003).

## Access path (for future connector)
- Preferred: partner API
- Endpoint candidates (method + URL):
  - SAM.gov Contract Opportunities API: https://open.gsa.gov/api/contract-opportunities-api/
  - Entity Management API (registration)
- Auth: API key (free tier limits)
- Pagination: API-specific offset/limit

## Job list / page structure (if known)
- Content-Type: varies
- Structure: JSON opportunity objects

## Field map sketch → RawJob
| Source | RawJob | Notes |
|--------|--------|-------|
| title, NAICS, placeOfPerformance | procurement context | US federal opportunities |

## Geo / role fit
- Countries: United States
- Fit for FMI Demand Compass: reference, FX, taxonomy, procurement context, or import — **not** primary vacancy KPIs unless explicitly jobs.

## Gaps / next step
- Register key; rate limits; not staffing orders.
