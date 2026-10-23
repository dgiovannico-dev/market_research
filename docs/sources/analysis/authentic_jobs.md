# Authentic Jobs (`authentic_jobs`)

| Field | Value |
|-------|-------|
| Analysis | DONE |
| collection_mode | feed |
| Collector file | `backend/app/collectors/authentic_jobs.py` |
| Probed_at | 2026-10-21 |
| Sample_records | 21 |

## Endpoint
- Method / URL: GET `https://feeds.feedburner.com/AuthenticJobs` (FeedBurner mirror; site `/rss` is editorial)
- Auth: None
- Query / body params: none; client filter; max `MAX_RECORDS` (50)
- Pagination: Single RSS feed
- Rate limit / ToS notes: Only items with `/jobs/` in link kept

## Payload / page structure
- Content-Type: RSS/XML
- Path to job list: `/rss/channel/item[]`
- Per-item keys (RSS): `title`, `link`, `description`, `pubDate`
- Nested paths that matter: title `"Company: Role"`; job id from URL path `/jobs/{id}`

## Field map → RawJob
| Source path | RawJob field | Transform / notes |
|-------------|--------------|-------------------|
| URL path `/jobs/(\d+)` | source_job_id | regex or fallback link |
| `link` | url | http→https upgrade |
| title after `:` | title | |
| title before `:` | company | |
| `description` | description | strip HTML |
| — | location | constant `"Remote/US"` |
| `pubDate` | published_at | RFC822 |
| — | salary_text | `None` |
| — | tags | empty |
| — | job_type | `None` |
| — | remote_hint | always `True` (assumed) |

## Gaps / precision risks
- Feed may mix non-job items (filtered by URL pattern)
- Cap 50 records
- Location not from feed (hard-coded)
- `raw` minimal `{title, link}`

## Live sample (redacted)
```json
{"title": "CEEK VR INC: Backend Engineer", "link": "https://authenticjobs.com/jobs/31742", "description": "<p>Role summary…truncated ~200 chars</p>"}
```
