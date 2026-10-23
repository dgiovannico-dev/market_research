# StepStone (catalog_id=28)

| Field | Value |
|-------|-------|
| Analysis | PARTNER_ONLY |
| Category | A |
| verification_status | NEEDS_CREDENTIALS |
| access_mode | partner_api |
| connector_key | — |

## Official / docs
- Official: https://www.stepstone.com/
- Developer: commercial XML/JSON feeds for publishers (StepStone Group partner desk).
- Terms: `/jobs/rss` probed as HTML — not used ([CREDENTIALED_CONNECTORS](../CREDENTIALED_CONNECTORS.md)).

## Access path (for future connector)
- Preferred: licensed job feed (DE/AT/BE/NL variants).
- Endpoint candidates: partner FTP/HTTPS feed URL (contractual).
- Auth: feed credentials + IP allowlist common.
- Pagination: full dump or delta files.

## Field map sketch → RawJob
| Source | RawJob | Notes |
|--------|--------|-------|
| external id | source_job_id | |
| link | url | |
| location | location | DACH strong |

## Geo / role fit
- Countries: DACH + EU StepStone brands.
- Fit for FMI Demand Compass: **Medium** if feed affordable — complements Bundesagentur, Jobindex, NFJ.

## Gaps / next step
- Sales/partner quote; do not scrape StepStone sites.
