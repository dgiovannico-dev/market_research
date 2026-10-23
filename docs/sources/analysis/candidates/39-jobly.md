# Jobly (catalog_id=39)

| Field | Value |
|-------|-------|
| Analysis | PARTNER_ONLY |
| Category | A |
| verification_status | UNDER_REVIEW |
| access_mode | unknown |
| connector_key | — |

## Official / docs
- Official: https://www.jobly.fi/
- Docs / developer: https://jobly.almamedia.fi/api/ (employer job **import** API)
- Terms / robots notes: Documented API is for employers/ATS to **add/update/delete** listings (XML POST). Not a public job search/download API.

## Access path (for future connector)
- Preferred: none for consumer ingest; employer API is outbound-only
- Endpoint candidates (method + URL):
  - `POST https://www.jobly.fi/api/v1/job?key={APIKEY}&action=add` (XML body, one job)
  - `POST https://www.jobly.fi/api/v1/job?key={APIKEY}&action=delete&id={job_id}`
- Auth: API key query param; optional IP allowlist + credit check on `uid`
- Pagination: N/A (write API)

## Job list / page structure (if known)
- Content-Type: `application/xml` request bodies (employer)
- Path to items / selectors: N/A for ingest
- Key fields observed or documented: unique job id in XML, location, salary, skills, application deadline (Alma Media spec)

## Field map sketch → RawJob
| Source | RawJob | Notes |
|--------|--------|-------|
| — | — | Wrong direction for collectors |

## Geo / role fit
- Countries: FI
- Fit for FMI Demand Compass: FI listings — use duunitori or other FI public sources already in catalog; Jobly only if Alma grants read feed

## Gaps / next step
- Ask Alma Career integrations for **read** syndication feed (if any)
- Do not scrape jobly.fi HTML; no authorized search API documented
