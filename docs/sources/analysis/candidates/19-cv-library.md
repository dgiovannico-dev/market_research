# CV-Library (catalog_id=19)

| Field | Value |
|-------|-------|
| Analysis | PARTNER_ONLY |
| Category | A |
| verification_status | UNDER_REVIEW |
| access_mode | unknown |
| connector_key | — |

## Official / docs
- Official: https://www.cv-library.co.uk/
- Docs / developer: https://www.cv-library.co.uk/developers/job-search-api ; https://www.cv-library.co.uk/developers/job-view-api
- Terms / robots notes: APIs explicitly **not for bulk download**; affiliate XML feeds require partner agreement and 24h refresh rules

## Access path (for future connector)
- Preferred: partner API (search JSON) or authorized XML/CSV affiliate feed
- Endpoint candidates (method + URL):
  - `GET https://www.cv-library.co.uk/search-jobs-json?key={KEY}&q={keywords}&geo={place}&distance={mi}&perpage=25&offset=0`
  - `GET https://partners.cv-library.co.uk/api/v1/jobs/{id}?key={KEY}`
  - Affiliate XML/CSV feed URL issued by partners@cv-library.co.uk
- Auth: partner `key` (query param)
- Pagination: `offset` + `perpage` (25/50/75/100) or `limit`; 404 past end

## Job list / page structure (if known)
- Content-Type: `application/json; charset=utf-8`
- Path to items / selectors: `jobs[]` array in search response
- Key fields observed or documented: agency block, applications, title, location, salary, url, posted date (see developer docs)

## Field map sketch → RawJob
| Source | RawJob | Notes |
|--------|--------|-------|
| job id | source_job_id | |
| job url | url | |
| title | title | |
| agency.title / employer | company | |
| description snippet | description | full via job-view API |
| location | location | |
| posted | published_at | |
| salary fields | salary_text | |

## Geo / role fit
- Countries: GB (UK)
- Fit for FMI Demand Compass: Good UK coverage with partner key; align with affiliate ToS (no unauthorized redistribution to Indeed/LinkedIn/DWP)

## Gaps / next step
- Email partners@cv-library.co.uk for API key and feed terms
- Probe search JSON under partner agreement; respect “no bulk download” scope (search-mode collector only)
