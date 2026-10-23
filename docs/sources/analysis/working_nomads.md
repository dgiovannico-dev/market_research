# Working Nomads (`working_nomads`)

| Field | Value |
|-------|-------|
| Analysis | DONE |
| collection_mode | dump |
| Collector file | `backend/app/collectors/working_nomads.py` |
| Probed_at | 2026-10-21 |
| Sample_records | 44 |

## Endpoint
- Method / URL: GET `https://www.workingnomads.com/api/exposed_jobs/`
- Auth: None
- Query / body params: none on wire; optional client filter on title/description
- Pagination: None (full array)
- Rate limit / ToS notes: User-Agent `FMI-MarketIntel/1.0`

## Payload / page structure
- Content-Type: `application/json`
- Path to job list: root array
- Per-item keys (list all top-level keys seen on one sample item): `category_name`, `company_name`, `description`, `location`, `pub_date`, `tags`, `title`, `url`
- Nested paths that matter: also accepts `published` alias for date (code path)

## Field map → RawJob
| Source path | RawJob field | Transform / notes |
|-------------|--------------|-------------------|
| `id` / `url` / `title` | source_job_id | first available |
| `url` | url | |
| `title` | title | |
| `company_name` / `company` | company | |
| `description` | description | HTML common |
| `location` | location | default `"Remote"` |
| `pub_date` / `published` | published_at | ISO8601 |
| `salary` | salary_text | if present (not in live sample keys) |
| `tags` | tags | |
| — | job_type | not mapped |
| — | remote_hint | always `True` |

## Gaps / precision risks
- No stable numeric id in sample payload; dedup uses URL/title fallback
- `category_name` not mapped to tags
- Client-side query only
- HTML descriptions; no plain-text strip

## Live sample (redacted)
```json
{"url": "https://www.workingnomads.com/job/go/1958438/", "title": "Senior DevOps Engineer", "company_name": "Lemon.io", "pub_date": "2026-10-...", "location": "Remote", "description": "<HTML truncated ~200 chars>"}
```
