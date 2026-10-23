# Randstad (catalog_id=70)

| Field | Value |
|-------|-------|
| Analysis | PARTNER_ONLY |
| Category | C |
| verification_status | UNDER_REVIEW |
| access_mode | website_or_feed |
| connector_key | — |

## Official / docs
- Official: https://www.randstad.com/
- Careers / job search: https://www.randstad.com/jobs/
- Docs / developer: none for public global job bulk API
- Terms / robots notes: Large staffing group (ADR-003). Country sites may syndicate to job boards; no verified public RSS/API for aggregators.

## Access path (for future connector)
- Preferred: Randstad enterprise XML/integration (country-specific where offered)
- Underlying employer postings: [Greenhouse](../greenhouse.md), [Lever](../lever.md), [SmartRecruiters](../smartrecruiters.md), [Workday Careers](88-workday-careers.md)
- Endpoint candidates (method + URL): none verified public bulk
- Auth: n/a until partnership
- Pagination: n/a

## Job list / page structure (if known)
- Content-Type: HTML / SPA on randstad.* regional domains
- No documented public REST or Atom/RSS job catalog for third parties

## Field map sketch → RawJob
| Source | RawJob | Notes |
|--------|--------|-------|
| Partner export (TBD) | all fields | After authorized schema |

## Geo / role fit
- Countries: global (EU, US, APAC strong)
- Fit for FMI Demand Compass: indirect; many reqs map to client ATS already crawlable

## Gaps / next step
- Engage Randstad integration teams for XML feed terms if required
- Avoid HTML scrape; dedupe against Adzuna/Reed syndication where present
