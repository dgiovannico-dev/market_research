# Indeed (catalog_id=10)

| Field | Value |
|-------|-------|
| Analysis | BLOCKED_TOS |
| Category | A |
| verification_status | NEEDS_CREDENTIALS |
| access_mode | publisher_api |
| connector_key | — |

## Official / docs
- Official: https://www.indeed.com/
- Developer: https://docs.indeed.com/ (Publisher / ATS integrations; not open bulk search).
- Terms: prohibits unauthorized scraping and automated extraction of job listings.

## Access path (for future connector)
- Preferred: **Indeed Publisher API** or formal data-licensing / partner program only.
- Endpoint candidates: partner-documented job sync or apply integrations (account-specific).
- Auth: publisher credentials / OAuth per Indeed contract.
- Pagination: per partner contract.

## Job list / page structure (if known)
- Public SERP HTML/JSON behind session — **not** authorized for FMI automation.

## Field map sketch → RawJob
| Source | RawJob | Notes |
|--------|--------|-------|
| partner job id | source_job_id | |
| url | url | |
| title, company, location | fields | when licensed |

## Geo / role fit
- Countries: global; overlaps many free aggregators already in repo.
- Fit for FMI Demand Compass: **Low priority** until licensed — prefer Jobicy, Himalayas, Adzuna (keyed), Careerjet, Jooble.

## Gaps / next step
- Mark BLOCKED_TOS for scrape/HTML paths per catalog notes and [ADR-003](../../decisions/ADR-003-authorized-connectors-only.md).
- Pursue only if commercial Indeed publisher agreement is approved.
