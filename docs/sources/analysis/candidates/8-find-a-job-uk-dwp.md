# Find a Job UK DWP (catalog_id=8)

| Field | Value |
|-------|-------|
| Analysis | IMPLEMENTED |
| Category | A |
| verification_status | NEEDS_CREDENTIALS |
| access_mode | api_key |
| connector_key | `findajob_dwp` |
| Collector sheet | [../findajob_dwp.md](../findajob_dwp.md) |

## Official / docs
- Official: https://findajob.dwp.gov.uk/
- Docs / developer: https://www.api.gov.uk/dwp/find-a-job/ (UK API Catalogue); internal PDF linked from api.gov.uk
- Terms / robots notes: Government service; API access via issued `api_id` / `api_key` (cross-government integration). Bulk employer upload is separate SFTP/XML (publisher path, not consumer ingest).

## Access path (for future connector)
- Preferred: public API (search) with registered credentials
- Endpoint candidates (method + URL):
  - `GET https://findajob.dwp.gov.uk/api/search?api_id={id}&api_key={key}&q={keywords}&w={location}&d={miles}&sf={min_salary}&html_description=1`
  - Location examples from catalogue: `w=Scotland`, `w=London`, postcode districts (e.g. `E1W`)
- Auth: query params `api_id`, `api_key` (issued by DWP/JCS)
- Pagination: not verified this pass; treat as search API with result caps per request (probe with credentials)

## Job list / page structure (if known)
- Content-Type: expected JSON or XML per DWP spec (catalogue examples show query-string search)
- Path to items / selectors: TBD after credential probe
- Key fields observed or documented: keywords, location (`w`), distance (`d`), min salary (`sf`), optional HTML description flag

## Field map sketch → RawJob
| Source | RawJob | Notes |
|--------|--------|-------|
| job id field (TBD) | source_job_id | from API response |
| canonical job URL | url | findajob.dwp.gov.uk detail link |
| title | title | |
| employer | company | |
| description | description | use `html_description=1` if supported |
| location text | location | UK |
| posted date | published_at | parse if present |
| salary text | salary_text | `sf` is search filter, not listing salary |

## Geo / role fit
- Countries: GB (primary)
- Fit for FMI Demand Compass: Strong UK public corpus; complements Reed jobseeker API where keyed; evidence tier likely high for gov listings once mapped

## Gaps / next step
- **Scaffolded** `findajob_dwp` (2026-10-21); set `FINDAJOB_DWP_API_ID` + `FINDAJOB_DWP_API_KEY`
- Probe live response schema/pagination; tweak `_as_list` / `_parse_item` if needed
- Promote ACTIVE only after succeeded CollectionRun with inserts
