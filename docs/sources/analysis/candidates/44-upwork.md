# Upwork (catalog_id=44)

| Field | Value |
|-------|-------|
| Analysis | DONE (scaffold) |
| Category | B |
| verification_status | NEEDS_CREDENTIALS |
| access_mode | oauth |
| connector_key | `upwork` |

## Official / docs
- Official: https://www.upwork.com/
- Docs / developer: https://www.upwork.com/developer/ — GraphQL at `https://api.upwork.com/graphql` (REST legacy sunset).
- Terms / robots notes: API keys require manual review (~1 week); personal/internal use only, no commercial redistribution, no sandbox. Eligibility includes verified ID, payment method, ≥$25k lifetime earnings/spend, 90% Job Success (freelancers/agencies), good standing ([Support: Request an API key](https://support.upwork.com/hc/en-us/articles/115015857647)).

## Access path (for future connector)
- Preferred: approved OAuth 2.0 app with scope **Read marketplace Job Postings**.
- Endpoint: `POST https://api.upwork.com/graphql` — `marketplaceJobPostingsSearch`.
- Auth: OAuth 2.0; `Authorization: Bearer`, optional `X-Upwork-API-TenantId` (`UPWORK_TENANT_ID`).
- Pagination: GraphQL `pagination_eq` (`after` / `first`).

## Connector scaffold
- File: `backend/app/collectors/upwork.py`
- Env: `UPWORK_OAUTH_TOKEN` (required), `UPWORK_TENANT_ID` (optional)
- Status stays **NEEDS_CREDENTIALS** until a live ingest with an approved key returns jobs.
- Public `/nx/jobs/search/` UI is not an authorized bulk ingest path (ADR-003).

## Field map sketch → RawJob
| Source | RawJob | Notes |
|--------|--------|-------|
| id / ciphertext | source_job_id | platform-specific ids |
| title | title | |
| description | description | scope-limited |
| createdDateTime | published_at | |
| ciphertext | url | `https://www.upwork.com/jobs/~{ciphertext}` |
| amount | salary_text | displayValue + currency |
| skills[].name | tags | |

## Geo / role fit
- Countries: global remote/gig.
- Fit for FMI Demand Compass: **Low–medium** — gig/project demand; viable only after key approval aligned with internal research (not a public open feed).

## Gaps / next step
- Submit API key request with internal FMI use case; set `UPWORK_OAUTH_TOKEN` and promote to ACTIVE after live evidence.
- Do not scrape job search HTML or use unofficial GraphQL without platform authorization.
