# Robert Half (catalog_id=69)

| Field | Value |
|-------|-------|
| Analysis | PARTNER_ONLY |
| Category | C |
| verification_status | UNDER_REVIEW |
| access_mode | website_or_feed |
| connector_key | — |

## Official / docs
- Official: https://www.roberthalf.com/
- Careers / job search: https://www.roberthalf.com/us/en/find-jobs
- Docs / developer: none for public third-party job API
- Terms / robots notes: US-centric staffing (ADR-003). Web job search only; no verified public bulk feed or RSS.

## Access path (for future connector)
- Preferred: Robert Half partner feed; client roles on employer Workday/Greenhouse boards
- Underlying employer postings: [Greenhouse](../greenhouse.md), [Lever](../lever.md), [SmartRecruiters](../smartrecruiters.md), [Workday Careers](88-workday-careers.md)
- Endpoint candidates (method + URL): none verified public bulk
- Auth: n/a until partnership
- Pagination: n/a

## Job list / page structure (if known)
- Content-Type: HTML job search; possible SPA-backed APIs not documented for external use
- Do not prescribe HTML scraping recipes (ADR-003)

## Field map sketch → RawJob
| Source | RawJob | Notes |
|--------|--------|-------|
| Partner export (TBD) | all fields | After authorized schema |

## Geo / role fit
- Countries: US primary; international Robert Half / Protiviti network
- Fit for FMI Demand Compass: US contract/perm mix; lower priority vs public boards where RH reposts duplicate ATS

## Gaps / next step
- Confirm RH Technology vertical has no public API (legal review)
- Request enterprise feed only if agency-specific coverage is needed
