# Findwork (`findwork`)

| Field | Value |
|-------|-------|
| Analysis | PARTIAL_SCAFFOLD |
| collection_mode | search |
| Collector file | `backend/app/collectors/findwork.py` |
| Credentials gate | `FINDWORK_API_KEY` (fail-closed without key) |

## Env keys

| Variable | Required | Role |
|----------|----------|------|
| `FINDWORK_API_KEY` | yes | Header `Authorization: Token …` |
| `FINDWORK_LOCATION` | no | Query `location` when set |

## Endpoint (from code)

- **Method / URL:** `GET https://findwork.dev/api/jobs/`
- **Headers:** `Authorization: Token <key>`, `Accept: application/json`, `User-Agent: FMI-MarketIntel/1.0`
- **Query:** `search`, `page` (1..2); optional `location`
- **Pagination:** stops when `results` empty or `next` absent
- **Fail-closed:** missing key → error; HTTP 401/403 → auth error

## Response shape (assumed)

- **Path to job list:** `results[]`
- **Pagination:** `next` (URL or flag — used as truthy stop condition)

## Field map → RawJob

| Source path | RawJob field | Transform / notes |
|-------------|--------------|-------------------|
| `id` | source_job_id | required |
| `url` or `job_url` | url | |
| `title` | title | fallback `"Untitled"` |
| `company_name` or `company` / `.name` / `.display_name` | company | |
| `description` or `text` | description | |
| `location` | location | also used for remote heuristic |
| `pub_date` or `created` | published_at | ISO; else now UTC |
| `salary` or `salary_min` | salary_text | stringified |
| `keywords` or `tags` | tags | list or single string |
| `employment_type` or `role_type` | job_type | |
| `remote` (bool) or `"remote"` in location | remote_hint | bool or heuristic |
| whole item | raw | |

## Gaps

- Live pagination (`next` shape) and max page behavior not verified without token
- Official field names may drift from doc comments at findwork.dev/developers
- Salary mapping prefers `salary` over min/max range formatting
