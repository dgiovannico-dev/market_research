# Arbeitnow (`arbeitnow`)

| Field | Value |
|-------|-------|
| Analysis | DONE |
| collection_mode | dump |
| Collector file | `backend/app/collectors/arbeitnow.py` |
| Probed_at | 2026-10-21 |
| Sample_records | 900 |

## Endpoint
- Method / URL: GET `https://www.arbeitnow.com/api/job-board-api`
- Auth: None
- Query / body params: `page` (1-based); optional client-side filter on `query` substring in title+tags
- Pagination: `links.next` until empty or `_MAX_PAGES` (3) ≈900 jobs
- Rate limit / ToS notes: Cap 3 pages by design (“stay polite”)

## Payload / page structure
- Content-Type: `application/json`
- Path to job list: `data[]`
- Per-item keys (list all top-level keys seen on one sample item): `company_name`, `created_at`, `description`, `job_types`, `location`, `remote`, `slug`, `tags`, `title`, `url`
- Nested paths that matter: `links.next`; `job_types` array joined for `job_type`

## Field map → RawJob
| Source path | RawJob field | Transform / notes |
|-------------|--------------|-------------------|
| `slug` / `url` | source_job_id | prefer slug |
| `url` | url | |
| `title` | title | |
| `company_name` | company | |
| `description` | description | often HTML |
| `location` | location | |
| `created_at` | published_at | Unix timestamp → UTC |
| — | salary_text | not in API payload |
| `tags` | tags | |
| `job_types` | job_type | comma-joined |
| `remote` | remote_hint | bool |

## Gaps / precision risks
- Partial dump (3 pages max); not `dump_complete`
- Client-side `query` filter only; no API search param
- No salary field
- `created_at` missing → `now()` fallback

## Live sample (redacted)
```json
{"slug": "senior-python-backend-engineer-bern-303737", "title": "Senior Python Backend Engineer", "company_name": "PROSTAFF Schweiz GmbH", "remote": true, "created_at": 1729..., "description": "<HTML truncated ~200 chars>"}
```
