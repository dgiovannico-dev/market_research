# Michael Page (catalog_id=68)

| Field | Value |
|-------|-------|
| Analysis | PARTNER_ONLY |
| Category | C |
| verification_status | UNDER_REVIEW |
| access_mode | website_or_feed |
| connector_key | — |

## Official / docs
- Official: https://www.michaelpage.com/ (PageGroup brand)
- Careers / job search: https://www.michaelpage.com/job-search
- Docs / developer: none for public bulk job API
- Terms / robots notes: PageGroup marketing/search UI (ADR-003). No authorized third-party bulk ingest. Prefer end-employer ATS where Page fills roles.

## Access path (for future connector)
- Preferred: PageGroup lawful import / enterprise feed
- Underlying employer postings: [Greenhouse](../greenhouse.md), [Lever](../lever.md), [SmartRecruiters](../smartrecruiters.md), [Workday Careers](88-workday-careers.md)
- Endpoint candidates (method + URL): none verified public bulk
- Auth: n/a until partnership
- Pagination: n/a

## Job list / page structure (if known)
- Content-Type: HTML; country-specific PageGroup domains
- No ADR-003-compliant global JSON/RSS job index identified

## Field map sketch → RawJob
| Source | RawJob | Notes |
|--------|--------|-------|
| Partner export (TBD) | all fields | After authorized schema |

## Geo / role fit
- Countries: global (UK, FR, DE, ES, IT, APAC, Americas via PageGroup)
- Fit for FMI Demand Compass: indirect; focus on end-employer boards for tech demand

## Gaps / next step
- Contact PageGroup for API/XML export policy
- Use Michael Page Salary Guide (catalog 142) only for analytics, not job ingest
