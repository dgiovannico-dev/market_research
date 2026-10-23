# Workable (catalog_id=87)

| Field | Value |
|-------|-------|
| Analysis | IMPLEMENTED |
| Category | D |
| verification_status | ACTIVE |
| access_mode | public_api_per_company |
| connector_key | `workable` |
| Collector sheet | [../workable.md](../workable.md) |

## Official / docs
- Official: https://www.workable.com/
- **Public careers / widget JSON (documented in Help):** https://help.workable.com/hc/en-us/articles/115012771647 — lists unauthenticated:
  - `GET https://www.workable.com/api/accounts/{subdomain}?details=true`
  - `GET https://www.workable.com/api/accounts/{subdomain}/locations`
  - `GET https://www.workable.com/api/accounts/{subdomain}/departments`
- **Widget host (equivalent payload):** `GET https://apply.workable.com/api/v1/widget/accounts/{slug}?details=true` — verified **200** on slug `huggingface` Oct 2026; redirects from `www.workable.com` URLs per Help
- **Account SPI (credentials):** https://developers.workable.com/ — `GET https://{subdomain}.workable.com/spi/v3/jobs` (scope `r_jobs`, Bearer token); reference https://workable.readme.io/reference/jobs — rate limit ~10 req / 10s per Help FAQ
- Terms: filter SPI to `state: published` for careers; public endpoints return published board only. ADR-003 — use documented JSON, not HTML scrape.

## Access path (for future connector)
- Preferred (multi-tenant market): public board JSON per known slug (`WORKABLE_SLUGS` env pattern, akin to Greenhouse boards)
- Endpoint candidates (method + URL):
  - `GET https://apply.workable.com/api/v1/widget/accounts/{slug}?details=false|true` — full board in one response; `details=true` adds `description`
  - `GET https://www.workable.com/api/accounts/{slug}?details=true` — same data per Workable Help
  - Tenant SPI: `GET https://{subdomain}.workable.com/spi/v3/jobs?limit=100` + paging `paging.next` when operator owns account
- Auth: none on public widget; Bearer token for SPI
- Pagination: **none** on widget (all jobs one payload); SPI uses `limit` (max 100) + `paging.next`

## Job list / page structure (if known)
- Content-Type: `application/json`
- Path to items: top-level `jobs[]`; envelope includes `name`, `description` (company)
- Key fields (widget): `title`, `shortcode`, `url`, `application_url`, `shortlink`, `department`, `city`, `state`, `country`, `telecommuting`, `employment_type`, `published_on`, `created_at`; `description` when `details=true`

## Field map sketch → RawJob
| Source | RawJob | Notes |
|--------|--------|-------|
| shortcode | source_job_id | `{slug}:{shortcode}` |
| url / application_url / shortlink | url | prefer public apply URL |
| title | title | |
| name (account) | company | board display name |
| city, state, country, telecommuting | location / remote_hint | assemble location_str if needed |
| description | description | only with `details=true` |
| published_on | published_at | |

## Geo / role fit
- Per-customer tenant boards (global employers); not a single national index
- Fit for FMI Demand Compass: **curated slug list** for target employers; SPI only when FMI holds Workable accounts

## Gaps / next step
- Add `WORKABLE_SLUGS` + collector in `ats_boards` pattern; cap per-tenant like Greenhouse
- Document 429 sensitivity on widget (backoff); invalid slug → 404 on apply host
