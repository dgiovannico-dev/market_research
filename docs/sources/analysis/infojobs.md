# InfoJobs (`infojobs`)

| Field | Value |
|-------|-------|
| Analysis | PARTIAL_SCAFFOLD |
| collection_mode | search |
| Collector file | `backend/app/collectors/infojobs.py` |
| Credentials gate | `INFOJOBS_CLIENT_ID` + `INFOJOBS_CLIENT_SECRET` |

## Env keys

| Variable | Required | Role |
|----------|----------|------|
| `INFOJOBS_CLIENT_ID` | yes | HTTP Basic username |
| `INFOJOBS_CLIENT_SECRET` | yes | HTTP Basic password |
| `INFOJOBS_COUNTRY` | no | Query `country` when set |
| `INFOJOBS_MAX_RESULTS` | no | Query `maxResults` (default 50) |

## Endpoint (from code)

- **Method / URL:** `GET https://api.infojobs.net/api/1/offer`
- **Auth:** httpx `auth=(client_id, client_secret)` (HTTP Basic)
- **Headers:** `Accept: application/json`
- **Query:** `q`, `page`, `maxResults`, `order=relevancia-desc`; optional `country`
- **Pagination:** up to 2 pages; stop on empty `offers` or `currentPage >= totalPages`

## Response shape (assumed)

- **Path to job list:** `offers[]`
- **Meta:** `totalPages`, `currentPage`

## Field map → RawJob

| Source path | RawJob field | Transform / notes |
|-------------|--------------|-------------------|
| `id` | source_job_id | required |
| `link` | url | |
| `title` | title | fallback `"Untitled"` |
| `author.name` | company | |
| `requirementMin` | description | not full job body |
| `city`, `province.value` | location | joined |
| `published` or `updated` | published_at | ISO; else now UTC |
| `salaryMin`, `salaryMax`, `salaryPeriod` | salary_text | `_pd_text` on dict `.value` fields |
| `category`, `subcategory` | tags | labels via `_pd_text` |
| `contractType` | job_type | `_pd_text` |
| _(none)_ | remote_hint | always `None` |
| whole item | raw | |

## Gaps

- App registration on developer.infojobs.net required; no live auth probe
- Bulk storage/redistribution may need partner agreement (see collector docstring)
- `requirementMin` may be shorter than full offer detail; detail API not used
- Country filter and relevancia ordering impact on corpus not verified
