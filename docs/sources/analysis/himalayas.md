# Himalayas (`himalayas`)

| Field | Value |
|-------|-------|
| Analysis | DONE |
| collection_mode | dump |
| Collector file | `backend/app/collectors/himalayas.py` |
| Probed_at | 2026-10-21 |
| Sample_records | 40 |

## Endpoint
- Method / URL: GET `https://himalayas.app/jobs/api`
- Auth: None
- Query / body params: `limit` from settings (`himalayas_page_limit`, default 40, max 100); optional `cursor`; client-side text filter on query
- Pagination: Up to 2 pages via `nextCursor`
- Rate limit / ToS notes: Public jobs API

## Payload / page structure
- Content-Type: `application/json`
- Path to job list: `jobs[]`
- Per-item keys (list all top-level keys seen on one sample item): `applicationLink`, `categories`, `companyLogo`, `companyName`, `companySlug`, `currency`, `description`, `employmentType`, `excerpt`, `expiryDate`, `guid`, `locationRestrictions`, `maxSalary`, `minSalary`, `parentCategories`, `pubDate`, `salaryPeriod`, `seniority`, `timezoneRestrictions`, `title`
- Nested paths that matter: `locationRestrictions` list → location string

## Field map → RawJob
| Source path | RawJob field | Transform / notes |
|-------------|--------------|-------------------|
| `guid` / `applicationLink` | source_job_id | require both guid and url |
| `applicationLink` | url | |
| `title` | title | |
| `companyName` | company | |
| `description` / `excerpt` | description | |
| `locationRestrictions` | location | join or `"Remote"` |
| `pubDate` | published_at | Unix epoch **or** ISO string |
| min/max + currency + period | salary_text | synthesized |
| `categories` | tags | stringified list |
| `employmentType` | job_type | |
| — | remote_hint | always `True` |

## Gaps / precision risks
- Rows missing `guid`/`applicationLink` skipped
- `pubDate` dual format (fixed 2026-10-20 per VALIDATION_REPORT)
- Client-side query only after fetch
- `seniority`, timezone restrictions not mapped

## Live sample (redacted)
```json
{"guid": "abc123", "title": "Sr Software Engineer - Veza", "companyName": "ServiceNow", "applicationLink": "https://...", "pubDate": 1729..., "employmentType": "Full-time", "description": "About the opportunity…truncated ~200 chars"}
```
