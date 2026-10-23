# US FPDS (catalog_id=156)

| Field | Value |
|-------|-------|
| Analysis | TODO_ACCESS |
| Category | H |
| verification_status | UNDER_REVIEW |
| access_mode | open_data_or_portal |
| connector_key | — |

## Official / docs
- Official: https://www.fpds.gov/
- Docs / developer: https://www.fpds.gov/
- Terms / robots notes: Use only authorized APIs/open data; procurement ≠ job postings (ADR-003).

## Access path (for future connector)
- Preferred: open data / atom
- Endpoint candidates (method + URL):
  - FPDS public reports and atom feeds (https://www.fpds.gov/)
- Auth: Varies by feed
- Pagination: Report parameters

## Job list / page structure (if known)
- Content-Type: varies
- Structure: XML/CSV award data

## Field map sketch → RawJob
| Source | RawJob | Notes |
|--------|--------|-------|
| contract value, agency | spend analytics | Historical awards |

## Geo / role fit
- Countries: US federal
- Fit for FMI Demand Compass: reference, FX, taxonomy, procurement context, or import — **not** primary vacancy KPIs unless explicitly jobs.

## Gaps / next step
- Awards ≠ open tenders; use for context only.
