# ECB Data API (catalog_id=143)

| Field | Value |
|-------|-------|
| Analysis | DOCUMENTED |
| Category | G |
| verification_status | ACTIVE |
| access_mode | public_api |
| connector_key | ecb_fx |

**Already covered:** [`../ecb_fx.md`](../ecb_fx.md) + `backend/app/fx/rates.py`.

## Official / docs
- Official: https://data.ecb.europa.eu/help/api/data
- Docs / developer: https://data.ecb.europa.eu/help/api/data
- Terms / robots notes: Use only authorized APIs/open data; procurement ≠ job postings (ADR-003).

## Access path (for future connector)
- Preferred: public API (SDMX-JSON)
- Endpoint candidates (method + URL):
  - GET https://data-api.ecb.europa.eu/service/data/EXR/D.USD.EUR.SP00.A?lastNObservations=1&format=jsondata
  - FMI: `GET /api/v1/fx/rates` (ECB fallback)
- Auth: None
- Pagination: SDMX constraints (`lastNObservations`, date range)

## Job list / page structure (if known)
- Content-Type: varies
- Structure: SDMX-JSON; extract observation for FX overlay

## Field map sketch → RawJob
| Source | RawJob | Notes |
|--------|--------|-------|
| observation | FX rate | Salary normalization only |

## Geo / role fit
- Countries: EUR reference; global FX pairs via EXR
- Fit for FMI Demand Compass: reference, FX, taxonomy, procurement context, or import — **not** primary vacancy KPIs unless explicitly jobs.

## Gaps / next step
- Not a job source; do not schedule as crawler.
