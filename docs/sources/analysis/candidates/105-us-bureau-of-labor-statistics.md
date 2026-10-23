# US Bureau of Labor Statistics (catalog_id=105)

| Field | Value |
|-------|-------|
| Analysis | DOCUMENTED |
| Role | `reference_not_jobs` — category **E**; not `RawJob` ingest |
| verification_status | UNDER_REVIEW |
| access_mode | api_key_optional |
| connector_key | — |

## Official / docs
- Official: https://www.bls.gov/data/
- Docs: https://www.bls.gov/data/
- Catalog note: Official statistics — import via datasets/API; do not mix incomparable series. Not wired as job connector.

## Access path (reference import)
- Preferred: BLS Public Data API v2 (free registration key recommended).
- `POST https://api.bls.gov/publicAPI/v2/timeseries/data/`
- Auth: per provider (api_key_optional).
- Series / tables: `LNS14000000` (unemployment rate), `CES0000000001` (employment), OES tables for wages.

## FMI use (context KPIs — not RawJob)
- US national context band; OES for occupation wage benchmarks (not live jobs).
- Store: `provider`, `series_id`, `geo`, `time`, `value`, `vintage`, `evidence_kind`.
- Never merge into observed job KPI numerators without explicit labeling (ADR-001).

## Field map → reference facts (not RawJob)
| Source | FMI field | Notes |
|--------|-----------|-------|
| Agency series / survey row | `reference_metric` | Numeric or categorical benchmark |
| Publication date | `vintage` | Survey year or release date |
| Geography | `geo` | ISO3166 / agency code |

## Geo / compliance
- US national (+ some metro in other programs).
- Lawful download/API only; no paywall or ToS-prohibited scraping (ADR-003).

## Gaps / next step
- API key in env; respect daily query limits.
