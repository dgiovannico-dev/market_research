# BambooHR (catalog_id=95)

| Field | Value |
|-------|-------|
| Analysis | IMPLEMENTED |
| Category | D |
| verification_status | UNDER_REVIEW |
| access_mode | public_api_per_company |
| connector_key | `bamboohr` |
| Collector sheet | [../bamboohr.md](../bamboohr.md) |

## Official / docs
- Official: https://www.bamboohr.com/
- **Open API (authenticated, official):** https://documentation.bamboohr.com/ — ATS section https://documentation.bamboohr.com/reference/applicant-tracking ; job summaries `GET /api/v1/applicant_tracking/jobs` (OAuth scope `hiring:applications`; company subdomain + API key/OAuth) — **tenant HR data, not a public job board index**
- **Public careers JSON (board widget; not in Open API reference):** industry-verified pattern used by hosted careers pages:
  - `GET https://{companyDomain}.bamboohr.com/careers/list`
  - `GET https://{companyDomain}.bamboohr.com/careers/{id}/detail`
  - Observed shape documented by third-party ATS references (e.g. https://conorscode.github.io/ats-api-reference/); BambooHR does not publish a separate “Careers Site API” page — treat as **public ATS board endpoint** per ADR-003, not HTML scrape
- Terms: Open API requires account permissions; invalid subdomains may **302** to marketing site rather than 404

## Access path (for future connector)
- Preferred (market research): public `careers/list` + optional `careers/{id}/detail` per known `{companyDomain}` slug list
- Endpoint candidates (method + URL):
  - `GET https://{slug}.bamboohr.com/careers/list` — `result[]` summaries, `meta.totalCount`
  - `GET https://{slug}.bamboohr.com/careers/{id}/detail` — `result.jobOpening` with HTML `description`, `datePosted`, `compensation`, richer `location`
  - Authenticated: `GET https://api.bamboohr.com/api/gateway.php/{companyDomain}/v1/applicant_tracking/jobs?statusGroups=Open` (operator credentials)
- Auth: none on public careers JSON; Basic (API key + `x`) or OAuth for Open API
- Pagination: none on list (single array); Open API uses query filters

## Job list / page structure (if known)
- Content-Type: `application/json` on careers endpoints
- Path to items: `result[]` on list; detail under `result.jobOpening`
- Key list fields: `id`, `jobOpeningName`, `departmentLabel`, `employmentStatusLabel`, `employmentType`, `location.city/state`, `isRemote`, `locationType`
- Key detail fields: `description`, `jobOpeningShareUrl`, `datePosted`, `compensation`, `minimumExperience`, `location.addressCountry`

## Field map sketch → RawJob
| Source | RawJob | Notes |
|--------|--------|-------|
| id | source_job_id | `{slug}:{id}` |
| jobOpeningShareUrl | url | from detail |
| jobOpeningName | title | |
| slug / host | company | no company name in JSON list |
| description | description | detail endpoint |
| location.* | location | sparse on list; prefer detail |
| datePosted | published_at | detail only |
| isRemote / locationType | remote_hint | |

## Geo / role fit
- SMB employers; one subdomain = one company (US/EU/global)
- Fit for FMI Demand Compass: **operator-provided slug list** (`BAMBOOHR_COMPANIES`), same pattern as Personio/Lever env tenants

## Gaps / next step
- Operator: probe from API egress (`BAMBOOHR_PROBE=… ./backend/scripts/probe_ats_tenants.sh`); only add **200 + non-empty** slugs to `BAMBOOHR_COMPANIES` — see [ATS_TENANTS.md](../../ATS_TENANTS.md) and [bamboohr.md](../bamboohr.md). Default includes `flyio` after 2026-10-21 probe (n=10); DC may still 503.
- Open API path = PARTNER_ONLY per tenant; do not use for bulk market index without credentials
- Promote catalog UNDER_REVIEW → ACTIVE after live inserts on operator egress
