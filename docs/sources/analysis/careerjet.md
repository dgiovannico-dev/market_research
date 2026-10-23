# Careerjet (`careerjet`)

| Field | Value |
|-------|-------|
| Analysis | PARTIAL_SCAFFOLD |
| collection_mode | search |
| Collector file | `backend/app/collectors/careerjet.py` |
| Credentials gate | `CAREERJET_API_KEY` + `CAREERJET_USER_IP` |

## Env keys

| Variable | Required | Role |
|----------|----------|------|
| `CAREERJET_API_KEY` | yes | HTTP Basic username (password empty) |
| `CAREERJET_USER_IP` | yes | Query `user_ip` (partner terms) |
| `CAREERJET_USER_AGENT` | no | Query `user_agent` + HTTP UA (default `FMI-MarketIntel/1.0`) |
| `CAREERJET_LOCALES` | no | Comma locales; default `it_IT,de_DE,de_CH,fr_CH,fr_LU` |
| `CAREERJET_LOCATION` | no | Query `location` |
| `CAREERJET_CONTRACT_TYPE` | no | Query `contract_type` (default `c` in config) |

## Endpoint (from code)

- **Method / URL:** `GET https://search.api.careerjet.net/v4/query`
- **Auth:** `Authorization: Basic base64("{api_key}:")`
- **Query:** `locale_code`, `keywords`, `page`, `page_size=50`, `user_ip`, `user_agent`, `sort=date`; optional `location`, `contract_type`
- **Pagination:** up to 2 pages per locale; stop on `pages` or short page
- **Special:** `type == "LOCATIONS"` → location resolution error, break locale loop

## Response shape (assumed)

- **Path to job list:** `jobs[]`
- **Meta:** `pages`, optional `type`, `message`

## Field map → RawJob

| Source path | RawJob field | Transform / notes |
|-------------|--------------|-------------------|
| `url` | source_job_id | **and** `url` (dedupe key is URL) |
| `title` | title | fallback `"Untitled"` |
| `company` | company | |
| `description` | description | |
| `locations` (list or scalar) | location | list joined with `", "` |
| `date` | published_at | RFC2822 or ISO via `_parse_date` |
| `salary` | salary_text | |
| _(none)_ | job_type | not mapped |
| _(none)_ | remote_hint | always `None` |
| whole item + `_careerjet_locale` | raw | locale injected |

## Gaps

- Publisher key and valid end-user IP not available for live probe
- `CAREERJET_USER_IP` must reflect real client IP per partner rules — not validated here
- LOCATIONS disambiguation flow not automated beyond error message
- Contract type default `c` may filter out permanent roles — behavior unverified live
