# JobTech Taxonomy API (catalog_id=174)

| Field | Value |
|-------|-------|
| Analysis | DOCUMENTED |
| Category | G |
| verification_status | VALIDATED |
| access_mode | public_api |
| connector_key | — |

In-repo: `backend/app/taxonomy/jobtech.py`; `GET /api/v1/taxonomy/jobtech/search`.

## Official / docs
- Official: https://taxonomy.api.jobtechdev.se/
- Docs / developer: https://taxonomy.api.jobtechdev.se/
- Terms / robots notes: Use only authorized APIs/open data; procurement ≠ job postings (ADR-003).

## Access path (for future connector)
- Preferred: public API
- Endpoint candidates (method + URL):
  - GET https://taxonomy.api.jobtechdev.se/v1/taxonomy/suggesters/autocomplete?query-string={q}&type=skill|occupation-name
- Auth: None
- Pagination: Autocomplete top-N

## Job list / page structure (if known)
- Content-Type: varies
- Structure: JSON suggester hits

## Field map sketch → RawJob
| Source | RawJob | Notes |
|--------|--------|-------|
| label, id | taxonomy term | SE labour market reference |

## Geo / role fit
- Countries: Sweden-focused taxonomy
- Fit for FMI Demand Compass: reference, FX, taxonomy, procurement context, or import — **not** primary vacancy KPIs unless explicitly jobs.

## Gaps / next step
- Complement ESCO; not Arbetsförmedlingen job search.
