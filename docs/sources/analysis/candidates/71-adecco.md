# Adecco (catalog_id=71)

| Field | Value |
|-------|-------|
| Analysis | PARTNER_ONLY |
| Category | C |
| verification_status | UNDER_REVIEW |
| access_mode | website_or_feed |
| connector_key | — |

## Official / docs
- Official: https://www.adecco.com/
- Careers / job search: https://www.adecco.com/en-us/job-search (country TLDs vary)
- Docs / developer: none for public global job bulk API
- Terms / robots notes: Adecco Group staffing (ADR-003). Some country postings appear on government exchanges; no verified public agency RSS/API for bulk ingest.

## Access path (for future connector)
- Preferred: country-level lawful feeds (government job exchanges where Adecco syndicates); enterprise partner XML
- Underlying employer postings: [Greenhouse](../greenhouse.md), [Lever](../lever.md), [SmartRecruiters](../smartrecruiters.md), [Workday Careers](88-workday-careers.md)
- Endpoint candidates (method + URL): none verified public bulk for adecco.com aggregator
- Auth: n/a until partnership
- Pagination: n/a

## Job list / page structure (if known)
- Content-Type: HTML / SPA per market
- No documented public JSON/RSS job index for third-party aggregation

## Field map sketch → RawJob
| Source | RawJob | Notes |
|--------|--------|-------|
| Partner export (TBD) | all fields | After authorized schema |

## Geo / role fit
- Countries: global (EU, US, LATAM strong)
- Fit for FMI Demand Compass: indirect; prefer national boards + employer ATS

## Gaps / next step
- Map EU markets where Adecco posts to official employment APIs (not adecco.com scrape)
- Request Adecco Group data partnership if agency layer is mandatory
