# Personio public career boards (`personio`)

| Field | Value |
|-------|-------|
| Analysis | DONE |
| collection_mode | dump |
| Collector file | `backend/app/collectors/ats_boards.py` (`PersonioCollector`) |
| Probed_at | 2026-10-21 |
| Sample_records | max 40/company (`MAX_PER_TENANT`); probe e.g. `chrono24` |

## Endpoint

- **Method / URL template:** `GET https://{company}.jobs.personio.de/search.json`
- **Auth:** none (public career board JSON)
- **Env tenant list:** `PERSONIO_COMPANIES` (CSV slugs; see `docs/sources/ATS_TENANTS.md`)
- **Pagination / MAX_PER_TENANT:** single array per company; ingest stops at **40** matched jobs
- **Job detail URL built as:** `https://{company}.jobs.personio.de/job/{id}?language=en`

## Payload / page structure

- **Content-Type:** `application/json`
- **Path:** root **array** of job objects (empty array → error `empty board`)
- **Per-item keys used:** `id`, `name`, `keywords`, `office` / `offices[0]`, `description`, `subcompany`, `department`, `employment_type`

## Field map → RawJob

| Source path | RawJob field | Transform / notes |
|-------------|--------------|-------------------|
| `{company}:{id}` | source_job_id | |
| constructed `/job/{id}` URL | url | not from payload |
| `name` | title | |
| `subcompany` else company slug | company | |
| `description` | description | only if non-empty string |
| `office` else `offices[0]` | location | |
| _(none)_ | published_at | **always collect-time UTC** (API dates unused) |
| `department` + keyword CSV (max 8) | tags | dept prepended |
| _(in raw only)_ | employment_type | not mapped to `job_type` |

## Gaps / precision risks

- **No published date** → soft-expire / freshness imprecise
- Description often short or empty on `search.json`
- 40/company cap; company slug vs `subcompany` inconsistency

## Live sample (redacted)

```json
{
  "id": 12345,
  "name": "Backend Engineer",
  "keywords": "Python, Django, Remote",
  "office": "Munich",
  "department": "Engineering",
  "subcompany": "Chrono24",
  "employment_type": "permanent",
  "description": "…"
}
```
