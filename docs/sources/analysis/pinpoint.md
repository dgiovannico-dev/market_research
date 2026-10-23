# Pinpoint postings.json (`pinpoint`)

| Field | Value |
|-------|-------|
| Analysis | DONE |
| collection_mode | dump |
| Collector file | `backend/app/collectors/pinpoint.py` |
| Probed_at | 2026-10-21 |
| Sample_records | max 40/subdomain (`MAX_PER_TENANT`) |

## Endpoint

- **Method / URL template:** `GET https://{subdomain}.pinpointhq.com/postings.json`
- **Auth:** none (public JSON)
- **Env tenant list:** `PINPOINT_SUBDOMAINS` (CSV; see `docs/sources/ATS_TENANTS.md`)
- **Pagination:** single response per subdomain; ingest stops at **40** matched jobs
- **Not used:** authenticated JSON:API (PARTNER_ONLY); legacy `jobs.json`

## Payload / page structure

- **Content-Type:** `application/json`
- **Path:** `data[]`
- **Per-item keys used:** `id`, `title`, `url`/`path`, `description`, `location`, `workplace_type(_text)`, `employment_type_text`, `compensation*`, `job.department|division|…`

## Field map → RawJob

| Source path | RawJob field | Transform / notes |
|-------------|--------------|-------------------|
| `{subdomain}:{id}` | source_job_id | |
| `url` else built from `path` | url | |
| `title` | title | |
| subdomain | company | no org name on public feed |
| `description` | description | HTML |
| `location.name` (skip stub `"l"`) | location | |
| _(none)_ | published_at | **collect-time UTC** (feed has no posted date) |
| `compensation` / min-max | salary_text | strong when visible |
| employment / workplace / dept | tags | |
| `employment_type_text` | job_type | |
| `workplace_type` | remote_hint | remote / onsite / hybrid |

## Gaps / precision risks

- **No published date** → soft-expire / freshness imprecise
- Some subdomains return demo/placeholder jobs — probe titles before adding
- Empty `data[]` is valid (200)

## Live sample (redacted)

```json
{
  "id": "223214",
  "title": "Data Engineer",
  "url": "https://made-tech.pinpointhq.com/en/postings/…",
  "location": {"name": "Any UK Office Hub (Bristol / London / …)"},
  "workplace_type": "hybrid",
  "compensation": "£41,500 - £55,000 / year",
  "job": {"department": {"name": "Technology"}}
}
```
