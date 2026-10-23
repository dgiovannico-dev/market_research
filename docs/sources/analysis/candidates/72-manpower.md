# Manpower (catalog_id=72)

| Field | Value |
|-------|-------|
| Analysis | PARTNER_ONLY |
| Category | C |
| verification_status | UNDER_REVIEW |
| access_mode | website_or_feed |
| connector_key | — |

## Official / docs
- Official: https://www.manpower.com/
- Careers / job search: https://www.manpower.com/en/job-search
- Docs / developer: none for public bulk job API (ManpowerGroup; see also Experis id 73)
- Terms / robots notes: Staffing brand (ADR-003). Web search only; no verified public RSS/API for aggregators.

## Access path (for future connector)
- Preferred: ManpowerGroup enterprise feed where offered
- Underlying employer postings: [Greenhouse](../greenhouse.md), [Lever](../lever.md), [SmartRecruiters](../smartrecruiters.md), [Workday Careers](88-workday-careers.md)
- Endpoint candidates (method + URL): none verified public bulk
- Auth: n/a until partnership
- Pagination: n/a

## Job list / page structure (if known)
- Content-Type: HTML / SPA on regional manpower.* sites
- Do not prescribe HTML scraping recipes (ADR-003)

## Field map sketch → RawJob
| Source | RawJob | Notes |
|--------|--------|-------|
| Partner export (TBD) | all fields | After authorized schema |

## Geo / role fit
- Countries: global (US, EU, APAC)
- Fit for FMI Demand Compass: indirect; Experis (73) covers IT vertical under same group

## Gaps / next step
- No scraper until feed agreement
- Dedupe Manpower vs Experis listings vs client ATS tenants
