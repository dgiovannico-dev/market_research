# Jobicy (`jobicy`)

| Field | Value |
|-------|-------|
| Analysis | DONE |
| collection_mode | dump |
| Collector file | `backend/app/collectors/jobicy.py` |
| Probed_at | 2026-10-21 |
| Sample_records | 100 |

## Endpoint
- Method / URL: GET `https://jobicy.com/api/v2/remote-jobs`
- Auth: None; attribution required (module docstring)
- Query / body params: `count=50`; optional `tag` from collector query; cursor via `cursor` / `nextCursor`
- Pagination: Up to `_MAX_PAGES` (2) while `hasMore`
- Rate limit / ToS notes: Free public API

## Payload / page structure
- Content-Type: `application/json`
- Path to job list: `jobs[]`
- Per-item keys (list all top-level keys seen on one sample item): `companyLogo`, `companyName`, `id`, `jobDescription`, `jobExcerpt`, `jobGeo`, `jobIndustry`, `jobLevel`, `jobSlug`, `jobTitle`, `jobType`, `pubDate`, `salaryCurrency`, `salaryMax`, `salaryMin`, `salaryPeriod`, `url`
- Nested paths that matter: `jobIndustry` / `jobType` may be scalar or list (flattened)

## Field map → RawJob
| Source path | RawJob field | Transform / notes |
|-------------|--------------|-------------------|
| `id` | source_job_id | skip if missing id/url |
| `url` | url | |
| `jobTitle` | title | |
| `companyName` | company | |
| `jobDescription` / `jobExcerpt` | description | prefer full description |
| `jobGeo` | location | default `"Remote"` |
| `pubDate` | published_at | ISO8601 |
| salaryMin/Max/Currency/Period | salary_text | single synthesized string |
| industry+level+type | tags | `_as_str_list` flatten |
| `jobType` | job_type | first list element |
| — | remote_hint | always `True` |

## Gaps / precision risks
- Capped at 2 pages (100 jobs in probe)
- Rows without `id`/`url` dropped silently
- `tag` param semantics vs free-text query unclear
- HTML in descriptions

## Live sample (redacted)
```json
{"id": 156127, "jobTitle": "Lead Machine Learning Scientist, Business Banking", "companyName": "Monzo", "url": "https://jobicy.com/jobs/156127-...", "jobIndustry": ["Data Science"], "pubDate": "2026-10-...", "jobDescription": "<truncated ~200 chars>"}
```
