# Remote OK (`remoteok`)

| Field | Value |
|-------|-------|
| Analysis | DONE |
| collection_mode | dump |
| Collector file | `backend/app/collectors/remoteok.py` |
| Probed_at | 2026-10-21 |
| Sample_records | 99 |

## Endpoint
- Method / URL: GET `https://remoteok.com/api`
- Auth: None; **attribution required** per API legal notice (docstring)
- Query / body params: optional `tag` = query with spaces → hyphens, lowercased
- Pagination: None (array response)
- Rate limit / ToS notes: Custom User-Agent; honor attribution on display

## Payload / page structure
- Content-Type: `application/json`
- Path to job list: root JSON **array** (first element may be metadata with `legal`)
- Per-item keys (list all top-level keys seen on one sample item): `apply_url`, `company`, `company_logo`, `date`, `description`, `epoch`, `id`, `location`, `logo`, `position`, `salary_max`, `salary_min`, `slug`, `tags`, `url`
- Nested paths that matter: `tags` string or array; salary min/max + implicit USD

## Field map → RawJob
| Source path | RawJob field | Transform / notes |
|-------------|--------------|-------------------|
| `id` | source_job_id | skip rows without `id` or with `legal` |
| `url` / `apply_url` | url | prefer `url` |
| `position` / `title` | title | |
| `company` | company | |
| `description` / `text` | description | |
| `location` | location | default `"Worldwide"` |
| `epoch` / `date` | published_at | epoch seconds or ISO; fallback `now()` |
| `salary` or min/max + `currency` | salary_text | synthesized range string |
| `tags` | tags | normalize str → single-element list |
| — | job_type | always `None` |
| — | remote_hint | always `True` |

## Gaps / precision risks
- No server-side query except `tag`; broad dump
- `job_type` not mapped though tags may imply role
- Fallback publish time hides bad dates
- Attribution obligation not enforced in ingestion layer

## Live sample (redacted)
```json
{"id": "1137548", "position": "Risk Analyst", "company": "Pavago", "epoch": 1792483205, "location": "Worldwide", "tags": ["python", "analyst"], "description": "<truncated ~200 chars>"}
```
