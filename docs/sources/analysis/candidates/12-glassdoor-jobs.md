# Glassdoor Jobs (catalog_id=12)

| Field | Value |
|-------|-------|
| Analysis | BLOCKED_TOS |
| Category | A |
| verification_status | NEEDS_CREDENTIALS |
| access_mode | partner_api |
| connector_key | — |

## Official / docs
- Official: https://www.glassdoor.com/Job/
- Developer: no stable public job-listing API for third-party aggregators; historical partner APIs limited.
- Terms: restricts scraping and competitive use of job content.

## Access path (for future connector)
- Preferred: commercial data license or Indeed/Glassdoor enterprise feed (if offered).
- Endpoint candidates: none verified for open self-serve ingest.
- Auth: partner credentials only.

## Job list / page structure (if known)
- HTML job search; not authorized without license.

## Field map sketch → RawJob
| Source | RawJob | Notes |
|--------|--------|-------|

## Geo / role fit
- Countries: US/EU focus; salary/review overlap not core FMI job-ingest goal.
- Fit for FMI Demand Compass: **No** unless licensed feed — low ROI vs free boards.

## Gaps / next step
- Keep NEEDS_CREDENTIALS; classify scrape attempts as BLOCKED_TOS ([ADR-003](../../decisions/ADR-003-authorized-connectors-only.md)).
