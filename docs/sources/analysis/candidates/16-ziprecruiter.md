# ZipRecruiter (catalog_id=16)

| Field | Value |
|-------|-------|
| Analysis | PARTNER_ONLY |
| Category | A |
| verification_status | NEEDS_CREDENTIALS |
| access_mode | partner_api |
| connector_key | — |

## Official / docs
- Official: https://www.ziprecruiter.com/
- Developer: ZipRecruiter partner / ATS integration programs (employer-side distribution).
- Terms: no public open job-search API for aggregators.

## Access path (for future connector)
- Preferred: partner feed or employer syndication agreement.
- Endpoint candidates: partner-documented job import/export (not public search).
- Auth: API keys issued to partners.
- Pagination: per partner spec.

## Field map sketch → RawJob
| Source | RawJob | Notes |
|--------|--------|-------|
| job id | source_job_id | |
| job_url | url | |

## Geo / role fit
- Countries: US-primary.
- Fit for FMI Demand Compass: **Optional** — pursue only with partner contract; US coverage partly via USAJOBS, Remote OK, etc.

## Gaps / next step
- Contact ZipRecruiter partnerships; no scrape path ([ADR-003](../../decisions/ADR-003-authorized-connectors-only.md)).
