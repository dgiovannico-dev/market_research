# Wanted (`wanted`)

| Field | Value |
|-------|-------|
| Analysis | DONE |
| collection_mode | search |
| Collector file | `backend/app/collectors/wanted.py` |
| Probed_at | 2026-10-21 |
| Sample_records | 40 (live collect, query `developer`) |

## Endpoint

- **Method / URL:** `GET https://www.wanted.co.kr/api/v4/jobs`
- **Auth:** none
- **Query params:** `country=kr`, `limit=40`, `query=<search>`
- **Pagination:** single page (`MAX_RECORDS=40`)
- **Detail URL pattern:** `https://www.wanted.co.kr/wd/{id}`

## Payload / page structure

- **Content-Type:** JSON object
- **Job list path:** `data[]`
- **Per-item keys:** `id`, `position`, `status`, `company`, `address`, `category_tags`, `annual_from`, `annual_to`
- **Filter:** skip rows where `status` is set and not `active`/`open` (case-insensitive)

## Field map → RawJob

| Source path | RawJob field | Transform / notes |
|-------------|--------------|-------------------|
| `id` | source_job_id | required |
| template | url | `DETAIL_URL.format(id=job_id)` |
| `position` | title | |
| `company.name` | company | |
| _(none)_ | description | always `None` (list API) |
| `address` | location | location, district, country; default `"South Korea"` |
| _(none)_ | published_at | **always now UTC** (not from API) |
| _(none)_ | salary_text | **always `None`** (`annual_*` = experience years) |
| `category_tags` | tags | `title` or string; max 15 |
| _(none)_ | job_type | `None` |
| _(none)_ | remote_hint | `None` |
| trimmed subset | raw | id, position, status, address, company, annual_from/to |

## Gaps / precision risks

- No description or real posted date on search endpoint
- `annual_from` / `annual_to` stored in raw but not mapped to salary
- Korea-only via fixed `country=kr`
- Blank query rejected

## Live sample (redacted)

```json
{
  "id": 393594,
  "position": "Full-Stack Developer(…)",
  "status": "active",
  "company": { "name": "…" },
  "address": { "location": "서울", "district": "동작구", "country": "한국" },
  "annual_from": 3,
  "annual_to": 7
}
```
