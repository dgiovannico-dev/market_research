# Wantedly (`wantedly`)

| Field | Value |
|-------|-------|
| Analysis | DONE |
| collection_mode | search |
| Collector file | `backend/app/collectors/wantedly.py` |
| Probed_at | 2026-10-21 |
| Sample_records | 10 (live collect, query `engineer`) |

## Endpoint

- **Method / URL:** `GET https://www.wantedly.com/api/v1/projects`
- **Auth:** none
- **Query params:** `q=<query>`, `page=1` (only first page)
- **Cap:** `MAX_RECORDS=40` client slice
- **Detail URL:** `https://www.wantedly.com/projects/{id}`

## Payload / page structure

- **Content-Type:** JSON object
- **Job list path:** `data[]` (Wantedly “projects”, treated as jobs)
- **Per-item keys:** `id`, `title`, `description`, `company`, `location`, `published_at`, `tags`, `looking_for`

## Field map → RawJob

| Source path | RawJob field | Transform / notes |
|-------------|--------------|-------------------|
| `id` | source_job_id | required |
| template | url | `/projects/{id}` |
| `title` | title | |
| `company.name` | company | |
| `description` | description | string only |
| `location` | location | fallback `"Japan"` |
| `published_at` | published_at | ISO parse |
| _(none)_ | salary_text | `None` |
| `tags`, `looking_for` | tags | max 15 |
| `looking_for` | job_type | also duplicated into tags |
| _(none)_ | remote_hint | `None` |
| trimmed subset | raw | id, title, dates, location, looking_for, company |

## Gaps / precision risks

- Only `page=1`; no further pagination
- Small result sets for narrow queries (live: 10 for `engineer`)
- No salary or remote signals
- Search-only (`missing_query_result` on blank query)

## Live sample (redacted)

```json
{
  "id": 2368531,
  "title": "防衛SE｜Forward Deployed Engineer",
  "company": { "name": "株式会社…" },
  "location": "東京都港区…",
  "published_at": "2026-03-11T17:42:31.063000+09:00",
  "looking_for": "ソフトウェアエンジニア"
}
```
