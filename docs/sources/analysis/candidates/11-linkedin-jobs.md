# LinkedIn Jobs (catalog_id=11)

| Field | Value |
|-------|-------|
| Analysis | BLOCKED_TOS |
| Category | A |
| verification_status | NEEDS_CREDENTIALS |
| access_mode | partner_api |
| connector_key | — |

## Official / docs
- Official: https://www.linkedin.com/jobs/
- Developer: LinkedIn Talent / Marketing APIs (restricted; job bulk search not generally available).
- Terms: User Agreement restricts scraping and unauthorized automated access.

## Access path (for future connector)
- Preferred: LinkedIn **Talent Solutions** or explicit data partnership (not self-serve open API).
- Endpoint candidates: partner-only job posting / apply integrations.
- Auth: OAuth + approved product scopes.
- Pagination: contract-specific.

## Job list / page structure (if known)
- Public job search is web/app only — scraping blocked for ADR-003.

## Field map sketch → RawJob
| Source | RawJob | Notes |
|--------|--------|-------|
| partner id | source_job_id | |
| apply URL | url | |

## Geo / role fit
- Countries: global professional market.
- Fit for FMI Demand Compass: **Defer** — high friction, ToS risk; use ATS boards + public APIs first.

## Gaps / next step
- Do not implement HTML or guest-API harvest ([ADR-003](../../decisions/ADR-003-authorized-connectors-only.md)).
- Revisit only with signed LinkedIn partner agreement.
