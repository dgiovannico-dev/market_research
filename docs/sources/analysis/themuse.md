# The Muse (`themuse`)

| Field | Value |
|-------|-------|
| Analysis | DONE |
| collection_mode | dump |
| Collector file | `backend/app/collectors/themuse.py` |
| Probed_at | 2026-10-21 |
| Sample_records | 20 |

## Endpoint
- Method / URL: GET `https://www.themuse.com/api/public/jobs`
- Auth: None (public API)
- Query / body params: fixed `page=0`, `category=Software Engineering`, `level=Senior Level`; **`query` not sent to API** (client filter only)
- Pagination: Single page fetch only (`page=0`)
- Rate limit / ToS notes: User-Agent header set

## Payload / page structure
- Content-Type: `application/json`
- Path to job list: `results[]`
- Per-item keys (list all top-level keys seen on one sample item): `categories`, `company`, `contents`, `id`, `levels`, `locations`, `model_type`, `name`, `publication_date`, `refs`, `short_name`, `tags`, `type`
- Nested paths that matter: `company.name`, `locations[].name`, `refs.landing_page`, `categories[].name`

## Field map → RawJob
| Source path | RawJob field | Transform / notes |
|-------------|--------------|-------------------|
| `id` | source_job_id | |
| `refs.landing_page` | url | |
| `name` | title | |
| `company.name` | company | |
| `contents` | description | HTML |
| `locations[].name` | location | comma-joined |
| `publication_date` | published_at | ISO8601 |
| — | salary_text | not mapped |
| `categories[].name` | tags | |
| — | job_type | not mapped |
| — | remote_hint | `None` (not inferred) |

## Gaps / precision risks
- Hard-coded senior SWE slice; misses other levels/categories
- No multi-page crawl
- Remote/hybrid not detected
- Optional `query` does not reduce API payload

## Live sample (redacted)
```json
{"id": 123, "name": "Sr. Staff Engineer (GenAI)", "company": {"name": "Uber"}, "publication_date": "2026-10-...", "refs": {"landing_page": "https://..."}, "contents": "<p>About the role…truncated ~200 chars</p>"}
```
