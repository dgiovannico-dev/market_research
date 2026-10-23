# findmethatdamjob.nl (`findmethatdamjob`)

| Field | Value |
|-------|-------|
| Analysis | DONE |
| collection_mode | search |
| Collector file | `backend/app/collectors/findmethatdamjob.py` |
| Probed_at | 2026-10-21 |
| Sample_records | 63 |

## Endpoint
- Method / URL: GET `https://gigsignal-api.fly.dev/api/jobs`
- Auth: None; docs at `https://findmethatdamjob.nl/docs/api/`
- Query / body params: `location=amsterdam` (NL-wide shortcut); **blank collector query → `missing_query` (no fetch)**
- Pagination: None (full list client-filtered); max 200 matches
- Rate limit / ToS notes: Server cache ~30m; not official UWV PES

## Payload / page structure
- Content-Type: `application/json`
- Path to job list: root **array** of job objects
- Per-item keys (from tests + API): `id`, `slug`, `title`, `apply_url`, `location`, `company_name`, `company_website`, `first_seen_at`, `gist`, `source_name`, `facts` (object)
- Nested paths that matter: `facts.skills[]`, `facts.seniority`, `facts.work_mode`, `facts.salary`

## Field map → RawJob
| Source path | RawJob field | Transform / notes |
|-------------|--------------|-------------------|
| `id` | source_job_id | |
| `apply_url` | url | required |
| `title` | title | |
| `company_name` | company | |
| `gist` | description | |
| `location` | location | default `"Netherlands"` |
| `first_seen_at` | published_at | ISO8601 |
| `facts.salary` | salary_text | str or dict join |
| skills + seniority | tags | |
| — | job_type | `None` |
| `facts.work_mode` | remote_hint | **`"remote"`/`"hybrid"`/`"onsite"` strings** (not bool) |

## Gaps / precision risks
- Search-mode: must supply query; downloads ~1280 NL jobs then substring match
- `remote_hint` type mismatch vs `RawJob` bool schema
- `raw` drops most payload fields
- Error when zero matches includes query string

## Live sample (redacted)
```json
{"id": "abc123", "title": "Senior Python Engineer", "apply_url": "https://example.com/careers/python", "company_name": "Acme BV", "location": "Amsterdam", "first_seen_at": "2026-10-20T10:00:00Z", "gist": "Backend role with Django…truncated", "facts": {"work_mode": "hybrid", "skills": ["Python"]}}
```
