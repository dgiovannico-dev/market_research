# okemprego (`okemprego`)

| Field | Value |
|-------|-------|
| Analysis | DONE |
| collection_mode | dump |
| Collector file | `backend/app/collectors/okemprego.py` |
| Probed_at | 2026-10-21 |
| Sample_records | 150 |

## Endpoint
- Method / URL: GET `https://www.okemprego.com/api/v1/jobs`
- Auth: None; cite canonical job URL (module docstring)
- Query / body params: `country` (default `PT` from `OKEMPREGO_COUNTRIES`), `category=it-data`, `perPage=50`, `page`, `sort=newest`; optional `q` search
- Pagination: Up to 3 pages per country; max 150 records
- Rate limit / ToS notes: PT/BR/AO focus; IT/data category default

## Payload / page structure
- Content-Type: `application/json`
- Path to job list: `data[]` with `pagination.totalPages`
- Per-item keys (typical API row; `raw` stores subset): `id`, `slug`, `title`, `url`, `company`, `description`, `city`, `location` (district/municipality objects), `country`, `postedAt`, `salary` (min/max/currency/period), `category`, `industry`, `experienceLevel`, `hoursType`, `contractType`, `skills[]`, `remote`
- Nested paths that matter: `location.municipality.name`, `location.district.name`, `salary.*`

## Field map → RawJob
| Source path | RawJob field | Transform / notes |
|-------------|--------------|-------------------|
| `id` / `slug` | source_job_id | |
| `url` | url | |
| `title` | title | |
| `company` | company | |
| `description` | description | |
| city + municipality + district + country | location | `_location()` |
| `postedAt` | published_at | ISO8601 |
| `salary` object | salary_text | min-max + currency/period |
| category, industry, levels, skills | tags | capped 15 |
| `hoursType` / `contractType` | job_type | |
| `remote` | remote_hint | `full`→True; hybrid/onsite→False |

## Gaps / precision risks
- Default category `it-data` excludes non-IT roles
- `q` param did not reduce count in probe (may be weak/unused server-side)
- `raw` omits description/skills (ingest uses top-level RawJob fields)
- Multi-country env expands scope beyond PT

## Live sample (redacted)
```json
{"id": "pt-123", "slug": "senior-python-developer-2", "title": "Senior Python Developer", "company": "Example Lda", "url": "https://www.okemprego.com/...", "postedAt": "2026-10-21T08:00:00Z", "remote": "hybrid", "description": "Responsibilities…truncated ~200 chars"}
```
