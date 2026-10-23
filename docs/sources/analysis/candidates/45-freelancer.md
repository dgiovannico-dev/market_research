# Freelancer (catalog_id=45)

| Field | Value |
|-------|-------|
| Analysis | IMPLEMENTED |
| Category | B |
| verification_status | NEEDS_CREDENTIALS |
| access_mode | oauth |
| connector_key | `freelancer` |
| Collector sheet | [../freelancer.md](../freelancer.md) |

## Official / docs
- Official: https://www.freelancer.com/
- Docs / developer: https://developers.freelancer.com/ — REST `0.1` API, OAuth 2.0, sandbox at `freelancer-sandbox.com`.
- Terms / robots notes: Register OAuth client; API use subject to developer terms and rate limits. Official Python SDK: `freelancersdk` ([GitHub](https://github.com/freelancer/freelancer-sdk-python)).

## Access path (for future connector)
- Preferred: OAuth 2.0 + REST project search (authorized marketplace API).
- Endpoint candidates (method + URL):
  - `GET https://www.freelancer.com/api/projects/0.1/projects/all/` — list/search active projects (query params per docs).
  - `GET https://www.freelancer.com/api/projects/0.1/projects/{project_id}/` — detail.
  - Sandbox host: `https://www.freelancer-sandbox.com/api/...` for integration tests.
- Auth: OAuth 2.0 (authorization code or client credentials for app-owned context per docs); bearer token on API calls.
- Pagination: offset/limit and filter objects per `search_projects` helpers in SDK.

## Job list / page structure (if known)
- Content-Type: `application/json`
- Items: project objects with title, description, budget, currency, skills/jobs, time_updated, seo_url.
- Key fields documented in API reference (projects namespace).

## Field map sketch → RawJob
| Source | RawJob | Notes |
|--------|--------|-------|
| id | source_job_id | |
| seo_url / url | url | absolute URL |
| title | title | |
| preview_description / description | description | |
| time_submitted / time_updated | published_at | prefer updated for active gigs |
| jobs / skills | tags | skill names |
| currency + budget | salary_* | fixed/hourly semantics |

## Geo / role fit
- Countries: global; location filters in search API.
- Fit for FMI Demand Compass: **Optional** gig/project overlay once OAuth app registered and terms checked for aggregation.

## Gaps / next step
- **Scaffolded** `freelancer` (2026-10-21); set `FREELANCER_OAUTH_TOKEN` (optional sandbox via `FREELANCER_API_BASE`)
- Validate live `projects/active` schema + ToS for analytics aggregation
- Promote ACTIVE only after succeeded CollectionRun with inserts
