# JobScout24 (catalog_id=27)

| Field | Value |
|-------|-------|
| Analysis | PARTNER_ONLY |
| Category | A |
| verification_status | UNDER_REVIEW |
| access_mode | unknown |
| connector_key | — |

## Official / docs
- Official: https://www.jobscout24.ch/
- Docs / developer: JobCloud affiliate program (shared with jobs.ch / jobup.ch) — affiliates@jobcloud.ch
- Terms / robots notes: Same JobCloud affiliate feed model; no standalone public API docs found

## Access path (for future connector)
- Preferred: partner XML/JSON feed (JobCloud)
- Endpoint candidates (method + URL): personalized feed URL after affiliate onboarding
- Auth: affiliate agreement
- Pagination: feed-specific

## Job list / page structure (if known)
- Content-Type: XML/JSON (partner)
- Path to items / selectors: per feed schema from JobCloud
- Key fields observed or documented: DE/FR/IT Swiss regions; workload percentages common on listings

## Field map sketch → RawJob
| Source | RawJob | Notes |
|--------|--------|-------|
| job id | source_job_id | |
| url | url | jobscout24.ch detail |
| title | title | |
| company | company | |
| location | location | |
| description | description | |
| employment_type | job_type | |
| salary_text | salary_text | |

## Geo / role fit
- Countries: CH (German-speaking Switzerland emphasis)
- Fit for FMI Demand Compass: Complements jobs.ch via single JobCloud partnership

## Gaps / next step
- Request JobCloud affiliate feed covering JobScout24 (can combine portals in one agreement)
- Mark NEEDS_CREDENTIALS once feed URL and license received
