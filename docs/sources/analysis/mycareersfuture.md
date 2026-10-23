# MyCareersFuture (`mycareersfuture`)

| Field | Value |
|-------|-------|
| Analysis | DONE |
| collection_mode | search |
| Collector file | `backend/app/collectors/mycareersfuture.py` |
| Probed_at | 2026-10-21 |
| Sample_records | 50 (live collect, query `software`) |

## Endpoint

- **Method / URL:** `GET https://api.mycareersfuture.gov.sg/v2/jobs`
- **Auth:** none (public government API)
- **Query params:** `limit=50`, `search=<query>` (`simplify_query_for` applied)
- **Pagination:** single request; cap `MAX_RECORDS=50`
- **Headers:** `User-Agent: FMI-MarketIntel/1.0`, `Accept: application/json`

## Payload / page structure

- **Content-Type:** JSON object
- **Job list path:** `results[]`
- **Per-item (mapped):** `uuid`, `title`, `description`, `postedCompany`, `address`, `salary`, `metadata`, `skills[]`, `positionLevels[]`, `employmentTypes[]`
- **Nested:** `postedCompany.name`, `salary.minimum|maximum|type.salaryType`, `metadata.createdAt|updatedAt`, `address.building|street|postalCode|overseasCountry`

## Field map → RawJob

| Source path | RawJob field | Transform / notes |
|-------------|--------------|-------------------|
| `uuid` | source_job_id | required; skip if missing |
| _(built)_ | url | `https://www.mycareersfuture.gov.sg/job/{uuid}` |
| `title` | title | fallback `"Untitled"` |
| `postedCompany.name` | company | |
| `description` | description | |
| `address` | location | join address fields; default `"Singapore"` |
| `metadata.createdAt` / `updatedAt` | published_at | ISO `Z`→offset; else now UTC |
| `salary` | salary_text | `{min}-{max} SGD/{period}` |
| `skills[].skill`, `positionLevels[].position` | tags | max 20 |
| `employmentTypes[].employmentType` | job_type | comma-joined |
| _(none)_ | remote_hint | always `None` |
| trimmed subset | raw | uuid, title, salary, metadata, postedCompany.name |

## Gaps / precision risks

- Blank query returns `missing_query_result()` (search-only)
- No pagination beyond first 50 hits
- `remote_hint` not inferred from payload
- Full job object not stored in `raw` (trimmed)

## Live sample (redacted)

```json
{
  "uuid": "70cd0fb4…",
  "title": "Software Quality Assurance and Support Engineer",
  "postedCompany": { "name": "THE SOFTWARE PRACTICE PTE. LTD" },
  "salary": { "minimum": 3500, "maximum": 5000, "type": { "salaryType": "Monthly" } },
  "metadata": { "createdAt": "2026-07-22T04:04:49+00:00" }
}
```
