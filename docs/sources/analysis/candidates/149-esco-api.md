# ESCO API (catalog_id=149)

| Field | Value |
|-------|-------|
| Analysis | DOCUMENTED |
| Category | G |
| verification_status | VALIDATED |
| access_mode | public_api |
| connector_key | — |

In-repo: `backend/app/taxonomy/esco.py`; `GET /api/v1/taxonomy/esco/search`.

## Official / docs
- Official: https://esco.ec.europa.eu/en/use-esco
- Docs / developer: https://ec.europa.eu/esco/api
- Terms / robots notes: Use only authorized APIs/open data; procurement ≠ job postings (ADR-003).

## Access path (for future connector)
- Preferred: public API
- Endpoint candidates (method + URL):
  - GET https://ec.europa.eu/esco/api/search?text={q}&language=en&type=occupation|skill|concept&limit=25
- Auth: None (User-Agent polite)
- Pagination: `limit` param (max 25 in FMI)

## Job list / page structure (if known)
- Content-Type: varies
- Structure: HAL JSON `_embedded.results`

## Field map sketch → RawJob
| Source | RawJob | Notes |
|--------|--------|-------|
| title, uri | taxonomy label/id | Skills/role enrichment |

## Geo / role fit
- Countries: EU multilingual taxonomy
- Fit for FMI Demand Compass: reference, FX, taxonomy, procurement context, or import — **not** primary vacancy KPIs unless explicitly jobs.

## Gaps / next step
- Reference only — not job postings or rates.
