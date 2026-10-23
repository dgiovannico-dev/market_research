# Hays (catalog_id=67)

| Field | Value |
|-------|-------|
| Analysis | PARTNER_ONLY |
| Category | C |
| verification_status | UNDER_REVIEW |
| access_mode | website_or_feed |
| connector_key | — |

## Official / docs
- Official: https://www.hays.com/
- Careers / job search: https://www.hays.com/job-search (regional Hays domains)
- Docs / developer: none for public bulk job API; salary guides are separate (catalog F)
- Terms / robots notes: Global staffing brand (ADR-003). No verified public aggregator API or RSS. Vacancies often duplicate client employer ATS postings.

## Access path (for future connector)
- Preferred: Hays enterprise XML/JSON feed or data partnership
- Underlying employer postings: [Greenhouse](../greenhouse.md), [Lever](../lever.md), [SmartRecruiters](../smartrecruiters.md), [Workday Careers](88-workday-careers.md) (`ats_boards` / tenant collectors)
- Endpoint candidates (method + URL): none verified public bulk
- Auth: n/a until partnership
- Pagination: n/a

## Job list / page structure (if known)
- Content-Type: HTML / SPA per country site; no documented global public job REST or RSS
- Do not prescribe HTML scraping recipes (ADR-003)

## Field map sketch → RawJob
| Source | RawJob | Notes |
|--------|--------|-------|
| Partner export (TBD) | all fields | After authorized schema |

## Geo / role fit
- Countries: global (strong UK, DE, AU, US regional sites)
- Fit for FMI Demand Compass: indirect agency layer; higher value via employer ATS connectors

## Gaps / next step
- Measure overlap with SmartRecruiters/Greenhouse tenants already on watchlist
- Request Hays digital team job export if bulk agency coverage is required
