# Swiss SIMAP (catalog_id=160)

| Field | Value |
|-------|-------|
| Analysis | TODO_ACCESS |
| Category | H |
| verification_status | UNDER_REVIEW |
| access_mode | open_data_or_portal |
| connector_key | — |

## Official / docs
- Official: https://www.simap.ch/
- Docs / developer: https://www.simap.ch/
- Terms / robots notes: Use only authorized APIs/open data; procurement ≠ job postings (ADR-003).

## Access path (for future connector)
- Preferred: portal + syndication
- Endpoint candidates (method + URL):
  - simap.ch public project search; syndication for registered users
- Auth: Optional account for alerts
- Pagination: Search filters

## Job list / page structure (if known)
- Content-Type: varies
- Structure: Portal HTML / PDF notices

## Field map sketch → RawJob
| Source | RawJob | Notes |
|--------|--------|-------|
| project title, CPV | CH procurement |

## Geo / role fit
- Countries: Switzerland
- Fit for FMI Demand Compass: reference, FX, taxonomy, procurement context, or import — **not** primary vacancy KPIs unless explicitly jobs.

## Gaps / next step
- Clarify machine-readable export; German/FR locales.
