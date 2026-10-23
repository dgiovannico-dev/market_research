# Internet Archive (catalog_id=167)

| Field | Value |
|-------|-------|
| Analysis | TODO_ACCESS |
| Category | I |
| verification_status | UNDER_REVIEW |
| access_mode | api |
| connector_key | — |

## Official / docs
- Official: https://archive.org/
- Docs / developer: https://archive.org/
- Terms / robots notes: Use only authorized APIs/open data; procurement ≠ job postings (ADR-003).

## Access path (for future connector)
- Preferred: public API
- Endpoint candidates (method + URL):
  - Wayback Availability API: https://archive.org/help/wayback_api.php
  - CDX search API for captures
- Auth: None (fair-use pacing)
- Pagination: CDX cursors

## Job list / page structure (if known)
- Content-Type: varies
- Structure: JSON/HTML snapshots

## Field map sketch → RawJob
| Source | RawJob | Notes |
|--------|--------|-------|
| archived HTML | historical evidence | Not live jobs |

## Geo / role fit
- Countries: Global web
- Fit for FMI Demand Compass: reference, FX, taxonomy, procurement context, or import — **not** primary vacancy KPIs unless explicitly jobs.

## Gaps / next step
- Use for provenance/archive only; primary jobs stay live connectors.
