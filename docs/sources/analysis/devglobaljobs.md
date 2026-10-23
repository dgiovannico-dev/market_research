# Dev Global Jobs (`devglobaljobs`)

| Field | Value |
|-------|-------|
| Analysis | DONE |
| collection_mode | dump |
| Collector file | `backend/app/collectors/devglobaljobs.py` |
| Probed_at | 2026-10-21 |
| Sample_records | 26 |

## Endpoint
- Method / URL: GET `https://devglobaljobs.com/api/v1/jobs`
- Auth: None; **visible “Powered by Dev Global Jobs” attribution** (API `meta.license`)
- Query / body params: `country` (ISO2 lower, default `lu,bg` via `DEVGLOBALJOBS_COUNTRIES`), `limit=50`, `offset`; optional `search` from collector query
- Pagination: 2 pages/country while `meta.hasMore`; max 200 records total
- Rate limit / ToS notes: 120 req/min/IP per module docstring

## Payload / page structure
- Content-Type: `application/json`
- Path to job list: `jobs[]` under object with `meta`
- Per-item keys (live sample): `category`, `closingDate`, `country`, `descriptionExcerpt`, `easyApply`, `featured`, `id`, `isEmployerPosted`, `jobType`, `location`, `organization`, `postedAt`, `salary`, `skillCategory`, `title`, `url`
- Nested paths that matter: `meta.hasMore`, `meta.total`

## Field map → RawJob
| Source path | RawJob field | Transform / notes |
|-------------|--------------|-------------------|
| `id` | source_job_id | |
| `url` | url | |
| `title` | title | |
| `organization` | company | |
| `descriptionExcerpt` | description | excerpt only, not full JD |
| `location` + request country | location | append `(ISO2)` |
| `postedAt` | published_at | ISO8601 |
| `salary` | salary_text | stringified |
| category, skillCategory, jobType | tags | |
| `jobType` | job_type | |
| category/location contains "remote" | remote_hint | bool or None |

## Gaps / precision risks
- `search=python` returned **0** jobs in probe (API filter may exclude all LU/BG rows)
- Partial dump per country/page caps
- Full description not available in list endpoint
- Country tagging prefers request ISO2 over payload `country` name

## Live sample (redacted)
```json
{"id": 165639161, "title": "Security Engineer, Bridge", "organization": "Example Co", "url": "https://devglobaljobs.com/...", "postedAt": "2026-10-21T12:00:00Z", "location": "Luxembourg", "jobType": "Full-time", "descriptionExcerpt": "We are looking for…truncated ~200 chars"}
```
