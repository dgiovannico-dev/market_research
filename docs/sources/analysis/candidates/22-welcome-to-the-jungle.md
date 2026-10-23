# Welcome to the Jungle (catalog_id=22)

| Field | Value |
|-------|-------|
| Analysis | PARTNER_ONLY |
| Category | A |
| verification_status | UNDER_REVIEW |
| access_mode | unknown |
| connector_key | — |

## Official / docs
- Official: https://www.welcometothejungle.com/
- Docs / developer: https://developers.welcomekit.co/jobs-api/jobs/list-all-jobs (WelcomeKit / WTTJ Solutions API)
- Terms / robots notes: Bulk job board sync requires **dedicated partnership** and OAuth scopes (`su_jobs_r`, etc.). Public website search is not an authorized bulk ingest path.

## Access path (for future connector)
- Preferred: partner API
- Endpoint candidates (method + URL):
  - `GET https://www.welcomekit.co/api/v1/external/jobs/all?status=published&per_page=100&page=1&updated_after=YYYY-MM-DD`
  - `GET https://www.welcomekit.co/api/v1/external/jobs/{reference}` (single job; `jobs_r` scope)
- Auth: `Authorization: Bearer {WK_API_KEY}`
- Pagination: `page`, `per_page`; filters `created_after`, `updated_after`, `published_after`, `contract_type`

## Job list / page structure (if known)
- Content-Type: `application/json`
- Path to items / selectors: jobs array in API response (per developer docs)
- Key fields observed or documented: status, contract_type, office/websites optional flags (`office=true`, `websites=true`)

## Field map sketch → RawJob
| Source | RawJob | Notes |
|--------|--------|-------|
| reference / id | source_job_id | |
| public URL field | url | from websites payload when enabled |
| name / title | title | |
| organization name | company | |
| description | description | |
| office location | location | FR/EU focus |
| published_at | published_at | |
| contract_type | job_type | |
| remote flags | remote_hint | if exposed |

## Geo / role fit
- Countries: FR primary; EU/international employers on WTTJ
- Fit for FMI Demand Compass: Good for EU tech/culture-fit roles once partnership approved

## Gaps / next step
- Apply for WTTJ Solutions partnership and API key with `su_jobs_r`
- Do not use unofficial scraper APIs; validate JSON schema on first authenticated probe
