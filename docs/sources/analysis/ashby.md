# Ashby Job Boards (`ashby`)

| Field | Value |
|-------|-------|
| Analysis | DONE |
| collection_mode | dump |
| Collector file | `backend/app/collectors/ats_boards.py` |
| Probed_at | 2026-10-21 |
| Sample_records | 40 max/tenant (`MAX_PER_TENANT`; probe `notion` lists 135 jobs) |

## Endpoint

- **Method / URL template:** `GET https://api.ashbyhq.com/posting-api/job-board/{org}`
- **Auth:** none (public job board API)
- **Env tenant list var:** `ASHBY_ORGS` (comma-separated org slugs; see `docs/sources/ATS_TENANTS.md`)
- **Pagination / MAX_PER_TENANT:** single response per org; ingest stops at **40 jobs per org** after optional query filter

## Payload / page structure

- **Content-Type:** `application/json`
- **Path to jobs array:** `jobs[]`
- **Per-item keys (read by collector):** `id`, `title`, `jobUrl`, `applyUrl`, `location` (string or `{name}`), `descriptionPlain`, `descriptionHtml` (live boards also expose `publishedAt`, `isRemote`, `department`, etc., **unused**)

## Field map → RawJob

| Source path | RawJob field | Transform / notes |
|-------------|--------------|-------------------|
| `id` + org slug | source_job_id | `f"{org}:{id}"` |
| `jobUrl` or `applyUrl` | url | first non-empty |
| `title` | title | fallback `"Untitled"` |
| org slug (env) | company | |
| `descriptionPlain` or `descriptionHtml` | description | plain preferred; else HTML string |
| `location` or `location.name` | location | string after dict unwrap |
| _(literal)_ | published_at | **always** `datetime.now(timezone.utc)` — API dates ignored |
| _(literal)_ | remote_hint | not set (`isRemote` on payload unused) |
| subset | raw | `{"id", "title", "org"}` |

Optional **query:** substring on `title` only.

## Gaps / precision risks

- **published_at** not taken from `publishedAt` — all jobs look “fresh” at collect time.
- **Remote / workplace** fields on payload not mapped.
- **40-job cap**; descriptions may be large HTML blobs.
- Org slug empty → collector error `ASHBY_ORGS empty`.

## Live sample (redacted)

```json
{
  "id": "1fc309c8-da20-4ff2-84c7-8b863ece2b0a",
  "title": "Software Engineer, AI Connections (Developer Platform)",
  "location": "San Francisco, California",
  "jobUrl": "https://jobs.ashbyhq.com/notion/1fc309c8-da20-4ff2-84c7-8b863ece2b0a",
  "applyUrl": "https://jobs.ashbyhq.com/notion/…/application",
  "publishedAt": "2026-08-24T14:44:49.699+00:00",
  "isRemote": true,
  "descriptionHtml": "<h1>Who We Are</h1><p>…</p>"
}
```
