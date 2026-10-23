# Jooble (`jooble`)

| Field | Value |
|-------|-------|
| Analysis | PARTIAL_SCAFFOLD |
| collection_mode | search |
| Collector file | `backend/app/collectors/jooble.py` |
| Credentials gate | `JOOBLE_API_KEY` |

## Env keys

| Variable | Required | Role |
|----------|----------|------|
| `JOOBLE_API_KEY` | yes | Path segment `/api/{key}` |
| `JOOBLE_LOCATION` | no | JSON body `location` when set |

## Endpoint (from code)

- **Method / URL:** `POST https://jooble.org/api/{JOOBLE_API_KEY}`
- **Headers:** `Content-Type: application/json`, `Accept: application/json`
- **Body:** `{ "keywords": "<query>", "page": 1 }` plus optional `location`
- **Pagination:** page 1 only
- **Fail-closed:** missing key → error; HTTP 401/403 → auth error

## Response shape (assumed)

- **Path to job list:** `jobs[]`

## Field map → RawJob

| Source path | RawJob field | Transform / notes |
|-------------|--------------|-------------------|
| `id` | source_job_id | required |
| `link` | url | |
| `title` | title | fallback `"Untitled"` |
| `company` | company | |
| `snippet` | description | |
| `location` | location | |
| `updated` | published_at | ISO; else now UTC |
| `salary` | salary_text | |
| `type` | job_type | |
| _(none)_ | remote_hint | always `None` |
| whole item | raw | |

## Gaps

- Jooble partner response schema not live-verified without API key
- Key embedded in URL path (logging/redaction risk in ops)
- Additional pages and rate limits not documented in collector
