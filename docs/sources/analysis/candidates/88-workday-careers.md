# Workday Careers (catalog_id=88)

| Field | Value |
|-------|-------|
| Analysis | IMPLEMENTED |
| Category | D |
| verification_status | ACTIVE |
| access_mode | public_api_per_tenant |
| connector_key | `workday` |
| Collector sheet | [../workday.md](../workday.md) |

## Official / docs
- Official: https://www.workday.com/
- Docs / developer: Workday HCM/careers product docs (tenant admin); public career sites use Workday-hosted CXS JSON (community-documented, not a single global API catalog).
- Terms / robots notes: Per-tenant `*.myworkdayjobs.com` sites; no global index. Use only published CXS endpoints on hosts the employer operates; respect site terms and rate limits.

## Access path (for future connector)
- Preferred: public JSON (CXS) per configured tenant + career site slug (same pattern as Greenhouse/Lever env tenant lists).
- Endpoint candidates (method + URL):
  - `POST https://{tenant}.wd{N}.myworkdayjobs.com/wday/cxs/{tenant}/{siteSlug}/jobs` — body JSON e.g. `{"appliedFacets":{},"limit":20,"offset":0,"searchText":""}` → `jobPostings[]`, `total`.
  - Job detail (full description): `GET https://{tenant}.wd{N}.myworkdayjobs.com/wday/cxs/{tenant}/{siteSlug}/job/{externalPath}` (path from listing `externalPath`).
- Auth: none on public external career sites (internal/unlisted sites differ).
- Pagination: `offset` + `limit` in POST body until `offset >= total`.

## Job list / page structure (if known)
- Content-Type: `application/json`
- Path to items: `jobPostings[]` (list); detail payload under `jobPostingInfo` / nested fields (tenant-specific).
- Key fields observed: `title`, `externalPath`, `locationsText`, `postedOn`, `bulletFields` (often requisition id).

## Field map sketch → RawJob
| Source | RawJob | Notes |
|--------|--------|-------|
| `bulletFields[0]` or hash of path | source_job_id | tenant-scoped |
| constructed job URL | url | from host + `externalPath` |
| `title` | title | |
| tenant token (env) | company | not always employer legal name |
| detail fetch | description | optional second request |
| `locationsText` | location | free text |
| `postedOn` | published_at | parse relative text or detail ISO if present |
| — | remote_hint | infer from text/facets if present |

## Geo / role fit
- Countries: worldwide where employers use Workday external career sites (strong enterprise / US / EU).
- Fit for FMI Demand Compass: high value per tenant for focus employers; requires curated `WORKDAY_TENANTS` (host, site slug, wd shard). No cross-tenant search.

## Gaps / next step
- **Shipped** `workday` collector + `WORKDAY_TENANTS` (2026-10-21); expand allowlist via `./backend/scripts/probe_ats_tenants.sh`.
- Optional: CXS job-detail GET for descriptions; better `postedOn` parsing.
- Do not scrape HTML job pages when CXS JSON is available.
