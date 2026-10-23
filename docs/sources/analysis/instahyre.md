# Instahyre (`instahyre`)

| Field | Value |
|-------|-------|
| Analysis | DONE |
| collection_mode | search |
| Collector file | `backend/app/collectors/instahyre.py` |
| Probed_at | 2026-10-21 |
| Sample_records | 35 (live collect, query `python`) |

## Endpoint

- **Method / URL:** `GET https://www.instahyre.com/api/v1/job_search/`
- **Auth:** none
- **Query params:** `q=<query>`, `offset=0`, `limit=40`
- **Pagination:** single page (`MAX_RECORDS=40`)

## Payload / page structure

- **Content-Type:** JSON object
- **Job list path:** `objects[]`
- **Per-item keys:** `id`, `title`, `candidate_title`, `public_url`, `employer`, `locations`, `reviewed_at`, `keywords`
- **Required for ingest:** both `id` and `public_url` must be present

## Field map → RawJob

| Source path | RawJob field | Transform / notes |
|-------------|--------------|-------------------|
| `id` | source_job_id | |
| `public_url` | url | absolute URL |
| `title` / `candidate_title` | title | fallback chain |
| `employer.company_name` / `name` | company | |
| _(none)_ | description | `None` (search API) |
| `locations` | location | default `"India"` |
| `reviewed_at` | published_at | ISO parse |
| _(none)_ | salary_text | `None` |
| `keywords` | tags | list or comma-split string; max 15 |
| _(none)_ | job_type / remote_hint | `None` |
| trimmed subset | raw | id, title, public_url, locations, reviewed_at |

## Gaps / precision risks

- No JD text on search endpoint
- `reviewed_at` may not equal first publish date
- Blank query rejected
- Employer object not fully preserved in `raw`

## Live sample (redacted)

```json
{
  "id": 447563,
  "title": "Staff Backend Engineer",
  "public_url": "https://www.instahyre.com/job-447563-…",
  "employer": { "company_name": "Amazon" },
  "locations": "Bangalore",
  "reviewed_at": "2026-10-21T12:34:51.260648+00:00",
  "keywords": ["Architecture", "backend", "go"]
}
```
