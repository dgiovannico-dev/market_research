# Workable careers widget (`workable`)

| Field | Value |
|-------|-------|
| Analysis | DONE |
| collection_mode | dump |
| Collector file | `backend/app/collectors/workable.py` |
| Probed_at | 2026-10-21 |
| Sample_records | max 40/slug (`MAX_PER_TENANT`) |

## Endpoint

- **Method / URL template:** `GET https://apply.workable.com/api/v1/widget/accounts/{slug}?details=true`
- **Auth:** none (public widget)
- **Env tenant list:** `WORKABLE_SLUGS` (CSV; see `docs/sources/ATS_TENANTS.md`)
- **Pagination:** none (full board one response); ingest stops at **40** matched jobs
- **Not used:** SPI v3 Bearer API (tenant-keyed)

## Payload / page structure

- **Content-Type:** `application/json`
- **Path:** `jobs[]`; envelope `name` = company
- **Per-item keys used:** `title`, `shortcode`, `url`/`shortlink`/`application_url`, `city`/`state`/`country`, `telecommuting`, `published_on`, `department`, `employment_type`, `description` (with `details=true`)

## Field map → RawJob

| Source path | RawJob field | Transform / notes |
|-------------|--------------|-------------------|
| `{slug}:{shortcode}` | source_job_id | |
| `url` / shortlink | url | |
| `title` | title | |
| envelope `name` | company | |
| `description` | description | when details=true |
| city, state, country | location | joined |
| `published_on` | published_at | date-only → UTC midnight |
| department + employment_type | tags | |
| `telecommuting` | remote_hint | boolean |

## Gaps / precision risks

- Many guessed brand slugs return **200 + `jobs:[]`** (empty board placeholder)
- Aggressive **HTTP 429** under parallel/burst load — serialize probes
- SPI path is PARTNER/tenant-only

## Live sample (redacted)

```json
{
  "name": "Hugging Face",
  "jobs": [{
    "title": "Open-Source Machine Learning Engineer - EMEA Remote",
    "shortcode": "81B46579FE",
    "city": "Paris",
    "country": "France",
    "telecommuting": true,
    "published_on": "2026-05-29"
  }]
}
```
