# Frankfurter (catalog_id=145)

| Field | Value |
|-------|-------|
| Analysis | DOCUMENTED |
| Category | G |
| verification_status | ACTIVE |
| access_mode | public_api |
| connector_key | frankfurter |

**Already covered:** [`../frankfurter.md`](../frankfurter.md) + `backend/app/fx/rates.py` (primary FX).

## Official / docs
- Official: https://www.frankfurter.app/
- Docs / developer: https://api.frankfurter.app/
- Terms / robots notes: Use only authorized APIs/open data; procurement ≠ job postings (ADR-003).

## Access path (for future connector)
- Preferred: public API
- Endpoint candidates (method + URL):
  - GET https://api.frankfurter.dev/v1/latest?from=EUR&to=USD,CHF,GBP
  - GET https://api.frankfurter.dev/v1/{date} (historical)
  - FMI: `GET /api/v1/fx/rates`
- Auth: None
- Pagination: N/A (latest or date path)

## Job list / page structure (if known)
- Content-Type: varies
- Structure: JSON `{base, date, rates}`

## Field map sketch → RawJob
| Source | RawJob | Notes |
|--------|--------|-------|
| rates[currency] | FX map | Not RawJob |

## Geo / role fit
- Countries: ECB-backed majors; global currency codes
- Fit for FMI Demand Compass: reference, FX, taxonomy, procurement context, or import — **not** primary vacancy KPIs unless explicitly jobs.

## Gaps / next step
- Primary FX; not vacancies.
