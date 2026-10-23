# Freelancer.com projects (`freelancer`)

| Field | Value |
|-------|-------|
| Analysis | PARTIAL_SCAFFOLD |
| collection_mode | search |
| Collector file | `backend/app/collectors/freelancer.py` |
| Probed_at | 2026-10-21 (scaffold; no live token) |
| Sample_records | max 50 / collect |

## Endpoint

- **Method / URL template:** `GET {FREELANCER_API_BASE}/projects/0.1/projects/active/`
- **Auth:** `Authorization: Bearer <token>` (+ `Freelancer-OAuth-V1` header)
- **Env:** `FREELANCER_OAUTH_TOKEN` (required); optional `FREELANCER_API_BASE` (default production)
- **Query:** `query`, `limit`, `offset`, `compact=true`
- **Not used:** HTML scrape of freelancer.com

## Payload / page structure

- Wrapper: `result.projects[]` (defensive fallback to top-level `projects`)
- Fields: `id`, `title`, `seo_url`, `preview_description`, `budget`, `currency`, `jobs`/`skills`, `time_updated`

## Field map → RawJob

| Source path | RawJob field | Transform / notes |
|-------------|--------------|-------------------|
| `id` | source_job_id | |
| `seo_url` → absolute | url | |
| `title` | title | |
| owner username (if present) | company | often absent in compact |
| `preview_description` | description | |
| `budget` + currency | salary_text | |
| `jobs`/`skills` names | tags | |
| `time_updated` | published_at | unix seconds |
| — | remote_hint | always True (marketplace gigs) |

## Gaps / precision risks

- OAuth app registration required; confirm ToS for aggregation/analytics
- Compact payloads may omit owner/description — expand params after first live probe
- Sandbox: set `FREELANCER_API_BASE=https://www.freelancer-sandbox.com/api`

## Live sample

_(none — `NEEDS_CREDENTIALS` until operator sets token and promote gate passes)_
