# Teamtailor (catalog_id=93)

| Field | Value |
|-------|-------|
| Analysis | IMPLEMENTED |
| Category | D |
| verification_status | ACTIVE |
| access_mode | public_api_per_host |
| connector_key | `teamtailor` |
| Collector sheet | [../teamtailor.md](../teamtailor.md) |

## Official / docs
- Official: https://www.teamtailor.com/
- Docs / developer: https://support.teamtailor.com/en/articles/5963369-use-our-teamtailor-api (JSON:API at `api.teamtailor.com`, key per account); public career feed documented as JSON Feed on career host.
- Terms / robots notes: Per-employer `{host}/jobs.json` is keyless where enabled; some sites disable feed. Partner API keys are tenant-scoped (Public/Internal/Admin).

## Access path (for future connector)
- Preferred: public JSON Feed on career host (no key); optional JSON:API with customer-issued key for same tenant only.
- Endpoint candidates (method + URL):
  - `GET https://{careerHost}/jobs.json` — JSON Feed 1.1 (`items[]`, `next_url` for pagination).
  - `GET https://api.teamtailor.com/v1/jobs` — JSON:API; headers `Authorization: Token token=…`, `X-Api-Version: YYYYMMDD` (per Teamtailor docs).
- Auth: none for `/jobs.json` where published; API key for JSON:API.
- Pagination: follow `next_url` until absent (~100 items/page typical).

## Job list / page structure (if known)
- Content-Type: `application/json`
- Path to items: `items[]` in feed; each item has `id`, `title`, `url`, `date_published`, `content_html`, `_jobposting` (schema.org JobPosting).
- Key fields: `_jobposting.identifier.value` (numeric id preferred), `jobLocation`, `hiringOrganization`.

## Field map sketch → RawJob
| Source | RawJob | Notes |
|--------|--------|-------|
| `_jobposting.identifier.value` or item `id` | source_job_id | host-scoped prefix |
| item `url` | url | |
| item `title` | title | |
| feed `title` or `_jobposting.hiringOrganization.name` | company | |
| item `content_html` | description | strip HTML |
| `_jobposting.jobLocation` | location | structured → string |
| item `date_published` | published_at | ISO-8601 |
| text / fields | remote_hint | rarely in feed; parse if needed |

## Geo / role fit
- Countries: strong EU/UK/Nordics; custom domains common.
- Fit for FMI Demand Compass: good per-tenant dump once career hosts are curated (`TEAMTAILOR_HOSTS`); no global discovery.

## Gaps / next step
- Probe feed enablement per host; handle `*.na.teamtailor.com` / AU regions.
- Live sample in repo probe script (e.g. `oatly.teamtailor.com/jobs.json` returns 200).
- JSON:API path only with explicit customer authorization (PARTNER_ONLY for cross-tenant).
