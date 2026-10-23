# AusTender (catalog_id=159)

| Field | Value |
|-------|-------|
| Analysis | DOCUMENTED |
| Category | H |
| verification_status | UNDER_REVIEW |
| access_mode | open_data_or_portal |
| connector_key | — |

## Official / docs
- Official: https://www.tenders.gov.au/
- Docs / developer: https://www.tenders.gov.au/
- Terms / robots notes: Use only authorized APIs/open data; procurement ≠ job postings (ADR-003).

## Access path (for future connector)
- Preferred: open data API
- Endpoint candidates (method + URL):
  - AusTender OCDS/API endpoints (https://www.tenders.gov.au/Reporting/OCds)
  - CN listing exports
- Auth: None for published OCDS
- Pagination: date-modified cursors

## Job list / page structure (if known)
- Content-Type: varies
- Structure: OCDS JSON

## Field map sketch → RawJob
| Source | RawJob | Notes |
|--------|--------|-------|
| tender | AU procurement |

## Geo / role fit
- Countries: Australia
- Fit for FMI Demand Compass: reference, FX, taxonomy, procurement context, or import — **not** primary vacancy KPIs unless explicitly jobs.

## Gaps / next step
- Filter ICT CPV; separate pipeline from jobs.
