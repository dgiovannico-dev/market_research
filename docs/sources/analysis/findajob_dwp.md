# Find a Job UK DWP (`findajob_dwp`)

| Field | Value |
|-------|-------|
| Analysis | PARTIAL_SCAFFOLD |
| collection_mode | search |
| Collector file | `backend/app/collectors/findajob_dwp.py` |
| Probed_at | 2026-10-21 (scaffold; no live keys) |
| Sample_records | max 50 / collect |

## Endpoint

- **Method / URL template:** `GET https://findajob.dwp.gov.uk/api/search`
- **Auth:** query `api_id` + `api_key` (cross-government credentials via UK API Catalogue)
- **Env:** `FINDAJOB_DWP_API_ID`, `FINDAJOB_DWP_API_KEY`, optional `FINDAJOB_DWP_LOCATION` → `w=`
- **Query:** `q=` keywords; `html_description=1`
- **Not used:** HTML scrape of findajob.dwp.gov.uk; SFTP/XML employer upload path

## Payload / page structure

- Expected JSON list under `results` / `jobs` / `items` / `vacancies` (defensive parser)
- Field map tolerates alternate employer/location keys until a keyed probe locks the schema

## Field map → RawJob

| Source path | RawJob field | Transform / notes |
|-------------|--------------|-------------------|
| `id` / `job_id` / `vacancy_id` / `reference` | source_job_id | |
| `url` / constructed `/details/{id}` | url | |
| `title` / `job_title` | title | |
| `employer` / `company` | company | |
| `description` / `html_description` | description | |
| `location` / `town` | location | UK |
| `posted` / `date_posted` | published_at | ISO if present else now |

## Gaps / precision risks

- Response schema not validated live (keys empty) — adjust parser after first credentialed probe
- Pagination not confirmed; single-page cap 50
- Catalogue page URL may move; confirm current DWP/JCS registration path before production

## Live sample

_(none — `NEEDS_CREDENTIALS` until operator sets keys and promote gate passes)_
