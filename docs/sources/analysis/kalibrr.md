# Kalibrr (`kalibrr`)

| Field | Value |
|-------|-------|
| Analysis | DONE |
| collection_mode | search |
| Collector file | `backend/app/collectors/kalibrr.py` |
| Probed_at | 2026-10-21 |
| Sample_records | 50 (live collect, query `software`) |

## Endpoint

- **Method / URL:** `GET https://www.kalibrr.com/api/job_board/search`
- **Auth:** none
- **Query params:** `limit=50`, `offset=0`, `text=<query>`
- **Pagination:** single page (`MAX_RECORDS=50`)
- **Client:** `follow_redirects=True`, timeout 45s

## Payload / page structure

- **Content-Type:** JSON object
- **Job list path:** `jobs[]`
- **Per-item keys:** `id`, `name`, `slug`, `company_name`, `description`, `company.code`, `company_info.code`, `google_location.address_components`, `activation_date`, `created_at`, `salary_shown`, `base_salary`, `maximum_salary`, `salary_currency`, `salary_interval`, `function`, `job_sds_skills`, `tenure`, `is_work_from_home`

## Field map → RawJob

| Source path | RawJob field | Transform / notes |
|-------------|--------------|-------------------|
| `id` | source_job_id | required |
| _(built)_ | url | `/c/{code}/jobs/{id}/{slug}` or `/jobs/{id}/{slug}` |
| `name` | title | |
| `company_name` | company | |
| `description` | description | string only |
| `google_location.address_components` | location | city, region, country |
| `activation_date` / `created_at` | published_at | ISO parse |
| salary fields | salary_text | only if `salary_shown`; `{lo}-{hi} {cur}/{interval}` |
| `function`, `job_sds_skills` | tags | max 15 |
| `tenure` | job_type | |
| `is_work_from_home` | remote_hint | bool if present |
| trimmed subset | raw | id, name, company, slug, dates, salary, WFH |

## Gaps / precision risks

- Search required; no full-board dump mode
- Salary omitted when `salary_shown` is false even if numbers exist
- Location empty if `google_location` missing

## Live sample (redacted)

```json
{
  "id": 55753,
  "name": "Quality Assurance Tester Work From Home",
  "company_name": "ThinkBIT Solutions",
  "is_work_from_home": true,
  "base_salary": 25000,
  "maximum_salary": 35000,
  "salary_currency": "PHP",
  "salary_interval": "month"
}
```
