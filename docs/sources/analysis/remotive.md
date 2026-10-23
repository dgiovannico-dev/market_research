# Remotive (`remotive`)

| Field | Value |
|-------|-------|
| Analysis | DONE |
| collection_mode | dump |
| Collector file | `backend/app/collectors/remotive.py` |
| Probed_at | 2026-10-21 |
| Sample_records | 10 |

## Endpoint
- Method / URL: GET `https://remotive.com/api/remote-jobs`
- Auth: None (public API)
- Query / body params: `category=software-dev` (fixed); optional `search` when collector `query` set
- Pagination: None (single response)
- Rate limit / ToS notes: Public JSON; use reasonable polling; no key documented

## Payload / page structure
- Content-Type: `application/json`
- Path to job list: `jobs[]`
- Per-item keys (list all top-level keys seen on one sample item): `candidate_required_location`, `category`, `company_logo`, `company_name`, `description`, `id`, `job_type`, `publication_date`, `salary`, `tags`, `title`, `url`
- Nested paths that matter: flat objects only; `tags` is string array

## Field map → RawJob
| Source path | RawJob field | Transform / notes |
|-------------|--------------|-------------------|
| `id` | source_job_id | `str()` |
| `url` | url | default `""` |
| `title` | title | default `"Untitled"` |
| `company_name` | company | |
| `description` | description | HTML/text as returned |
| `candidate_required_location` | location | geo eligibility string |
| `publication_date` | published_at | ISO8601 → UTC; fallback `now()` on parse fail |
| `salary` | salary_text | optional string |
| `tags` | tags | `list()` |
| `job_type` | job_type | e.g. full_time |
| — | remote_hint | always `True` |

## Gaps / precision risks
- Dump is scoped to `software-dev` only; other categories never fetched
- Invalid `publication_date` falls back to collection time (masks staleness)
- No pagination; full list size is API-defined
- Optional `search` param behavior not capped in collector

## Live sample (redacted)
```json
{"id": 2091158, "url": "https://remotive.com/remote-jobs/...", "title": "Software Engineer, AI Coding Tasks", "company_name": "Askable", "publication_date": "2026-10-...", "tags": ["python", "docker"], "description": "<truncated ~200 chars>"}
```
