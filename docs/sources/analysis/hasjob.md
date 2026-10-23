# Hasjob (`hasjob`)

| Field | Value |
|-------|-------|
| Analysis | DONE |
| collection_mode | dump |
| Collector file | `backend/app/collectors/hasjob.py` |
| Probed_at | 2026-10-21 |
| Sample_records | 16 (live collect, no query filter) |

## Endpoint

- **Method / URL:** `GET https://hasjob.co/`
- **Auth:** none
- **Query params:** `format=json` (JSON board dump)
- **Optional client filter:** lowercase `query` matched in `headline` or `company_name`
- **Cap:** `MAX_RECORDS=50`

## Payload / page structure

- **Content-Type:** JSON object
- **Job list paths:** `posts[]` **or** flattened `grouped[].posts[]`
- **Per-item keys:** `headline`, `company_name`, `location`, `url`, `date`
- **URL:** relative path → prefixed with `https://hasjob.co`

## Field map → RawJob

| Source path | RawJob field | Transform / notes |
|-------------|--------------|-------------------|
| `url` (path) | source_job_id | `str(path).strip("/")` |
| `url` | url | absolute if missing scheme |
| `headline` | title | |
| `company_name` | company | |
| _(none)_ | description | `None` |
| `location` | location | default `"India"` |
| `date` | published_at | ISO parse |
| _(none)_ | salary_text, tags, job_type, remote_hint | empty / `None` |
| trimmed subset | raw | headline, company, location, url, date |

## Gaps / precision risks

- Full dump often small (live: 16 posts); not a paginated national index
- No skills, salary, or body text
- `source_job_id` is URL path, not stable numeric id
- Query filter is substring only (client-side)

## Live sample (redacted)

```json
{
  "headline": "Automic Admin",
  "company_name": "Potentiam Ltd",
  "location": "Bangalore",
  "url": "/potentiam.co.uk/m3t8m",
  "date": "2026-10-19T11:55:35.484215+00:00"
}
```
