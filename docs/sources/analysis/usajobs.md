# USAJOBS (`usajobs`)

| Field | Value |
|-------|-------|
| Analysis | PARTIAL_SCAFFOLD |
| collection_mode | search |
| Collector file | `backend/app/collectors/usajobs.py` |
| Credentials gate | `USAJOBS_API_KEY` + `USAJOBS_USER_AGENT` (contact email) |

## Env keys

| Variable | Required | Role |
|----------|----------|------|
| `USAJOBS_API_KEY` | yes | Header `Authorization-Key` |
| `USAJOBS_USER_AGENT` | yes | Header `User-Agent` (email) |
| `USAJOBS_JOB_CATEGORY_CODE` | no | Query `JobCategoryCode` (e.g. `2210` IT) |

## Endpoint (from code)

- **Method / URL:** `GET https://data.usajobs.gov/api/search`
- **Headers:** `Host: data.usajobs.gov`, `User-Agent`, `Authorization-Key`, `Accept: application/json`
- **Query:** `Keyword`, `ResultsPerPage=50`, `Page=1`; optional `JobCategoryCode`
- **Pagination:** single page only in scaffold
- **Fail-closed:** missing key or user agent → error; HTTP 401/403 → auth error

## Response shape (assumed)

- **Path to job list:** `SearchResult.SearchResultItems[]`
- **Per row:** `MatchedObjectId`, `MatchedObjectDescriptor` (nested job fields)

## Field map → RawJob

| Source path | RawJob field | Transform / notes |
|-------------|--------------|-------------------|
| `MatchedObjectId` or `MatchedObjectDescriptor.PositionID` | source_job_id | skip if empty |
| `MatchedObjectDescriptor.PositionURI` | url | |
| `MatchedObjectDescriptor.PositionTitle` | title | fallback `"Untitled"` |
| `MatchedObjectDescriptor.OrganizationName` | company | |
| `UserArea.Details.JobSummary` or `MajorDuties` | description | list → newline-joined |
| `MatchedObjectDescriptor.PositionLocationDisplay` | location | |
| `PublicationStartDate` or `PositionStartDate` | published_at | ISO; else now UTC |
| _(none)_ | salary_text | not mapped |
| `PositionSchedule[0].Name` | job_type | if schedule is list of objects |
| _(none)_ | remote_hint | always `None` |
| whole row | raw | |

## Gaps

- Cannot verify live without API key and registered User-Agent email
- Only first page ingested; total result count and paging params not exercised
- Salary and telework fields exist in USAJOBS schema but are not mapped
