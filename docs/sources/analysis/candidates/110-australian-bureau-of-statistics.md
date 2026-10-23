# Australian Bureau of Statistics (catalog_id=110)

| Field | Value |
|-------|-------|
| Analysis | DOCUMENTED |
| Role | `reference_not_jobs` — category **E**; not `RawJob` ingest |
| verification_status | UNDER_REVIEW |
| access_mode | open_data |
| connector_key | — |

## Official / docs
- Official: https://www.abs.gov.au/
- Docs: https://www.abs.gov.au/
- Catalog note: Official statistics — import via datasets/API; do not mix incomparable series. Not wired as job connector.

## Access path (reference import)
- Preferred: ABS Data API (SDMX/JSON).
- ABS API documentation at abs.gov.au.
- Auth: per provider (open_data).
- Series / tables: Labour force, employment by industry (ANZSIC).

## FMI use (context KPIs — not RawJob)
- AU macro + industry employment context.
- Store: `provider`, `series_id`, `geo`, `time`, `value`, `vintage`, `evidence_kind`.
- Never merge into observed job KPI numerators without explicit labeling (ADR-001).

## Field map → reference facts (not RawJob)
| Source | FMI field | Notes |
|--------|-----------|-------|
| Agency series / survey row | `reference_metric` | Numeric or categorical benchmark |
| Publication date | `vintage` | Survey year or release date |
| Geography | `geo` | ISO3166 / agency code |

## Geo / compliance
- Australia.
- Lawful download/API only; no paywall or ToS-prohibited scraping (ADR-003).

## Gaps / next step
- Confirm API token requirements for high volume.
