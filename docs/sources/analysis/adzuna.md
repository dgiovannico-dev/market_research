# Adzuna (`adzuna`)

| Field | Value |
|-------|-------|
| Analysis | PARTIAL_SCAFFOLD |
| collection_mode | search |
| Collector file | `backend/app/collectors/adzuna.py` |
| Credentials gate | `credentials_present` requires `ADZUNA_APP_ID` + `ADZUNA_APP_KEY` |

## Env keys

| Variable | Required | Role |
|----------|----------|------|
| `ADZUNA_APP_ID` | yes | Query param `app_id` |
| `ADZUNA_APP_KEY` | yes | Query param `app_key` |
| `ADZUNA_COUNTRIES` | no | Comma-separated country codes; overrides single country |
| `ADZUNA_COUNTRY` | no | Default country when `ADZUNA_COUNTRIES` empty (default `gb`) |

## Endpoint (from code)

- **Method / URL:** `GET https://api.adzuna.com/v1/api/jobs/{country}/search/{page}`
- **Auth:** query params `app_id`, `app_key`
- **Query:** `results_per_page=50`, `what=<simplified query>`, `content-type=application/json`
- **Pagination:** pages `1..2` per country; stop when `len(results) < 50`
- **Countries:** `resolve_adzuna_countries(ADZUNA_COUNTRIES, ADZUNA_COUNTRY)`
- **Fail-closed:** missing keys → empty records + error; HTTP 401/403 → auth error

## Response shape (assumed)

- **Path to job list:** `results[]`

## Field map → RawJob

| Source path | RawJob field | Transform / notes |
|-------------|--------------|-------------------|
| `id` | source_job_id | required; skip if missing |
| `redirect_url` or `adref` | url | |
| `title` | title | fallback `"Untitled"` |
| `company.display_name` | company | if `company` is object |
| `description` | description | |
| `location.display_name` | location | if `location` is object |
| `created` | published_at | ISO; `Z`→`+00:00`; else now UTC |
| `salary_min`, `salary_max` | salary_text | joined `" - "` |
| `contract_type` or `contract_time` | job_type | |
| _(none)_ | remote_hint | always `None` |
| whole item + `_adzuna_country` | raw | country code injected |

## Gaps

- No live keyed probe in this pass; response keys and error bodies unverified
- Multi-country dedupe uses `source_job_id` only (same id across countries not tested)
- Redirect URLs vs stable job URLs not validated against Adzuna ToS
