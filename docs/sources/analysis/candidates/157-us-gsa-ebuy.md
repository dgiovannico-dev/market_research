# US GSA eBuy (catalog_id=157)

| Field | Value |
|-------|-------|
| Analysis | TODO_ACCESS |
| Category | H |
| verification_status | UNDER_REVIEW |
| access_mode | open_data_or_portal |
| connector_key | — |

## Official / docs
- Official: https://www.gsa.gov/
- Docs / developer: https://www.gsa.gov/
- Terms / robots notes: Use only authorized APIs/open data; procurement ≠ job postings (ADR-003).

## Access path (for future connector)
- Preferred: partner portal
- Endpoint candidates (method + URL):
  - GSA eBuy / Schedules — vendor login workflows
- Auth: GSA vendor credentials
- Pagination: N/A

## Job list / page structure (if known)
- Content-Type: varies
- Structure: Portal HTML / RFQ

## Field map sketch → RawJob
| Source | RawJob | Notes |
|--------|--------|-------|
| — | — | No public API; partner portal only |

## Geo / role fit
- Countries: US
- Fit for FMI Demand Compass: reference, FX, taxonomy, procurement context, or import — **not** primary vacancy KPIs unless explicitly jobs.

## Gaps / next step
- No public job-style API; partner-only.
