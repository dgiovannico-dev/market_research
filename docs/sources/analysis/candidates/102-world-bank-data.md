# World Bank Data (catalog_id=102)

| Field | Value |
|-------|-------|
| Analysis | DOCUMENTED |
| Role | `reference_not_jobs` — category **E**; not `RawJob` ingest |
| verification_status | UNDER_REVIEW |
| access_mode | open_data |
| connector_key | — |

## Official / docs
- Official: https://data.worldbank.org/
- Docs: https://data.worldbank.org/
- Catalog note: Official statistics — import via datasets/API; do not mix incomparable series. Not wired as job connector.

## Access path (reference import)
- Preferred: World Bank Open Data API v2.
- `GET https://api.worldbank.org/v2/country/{iso}/indicator/{code}?format=json`
- Auth: per provider (open_data).
- Series / tables: `SL.UEM.TOTL.ZS` (unemployment), `SL.TLF.TOTL.IN` (labour force).

## FMI use (context KPIs — not RawJob)
- Emerging-market context KPIs; coarse granularity only.
- Store: `provider`, `series_id`, `geo`, `time`, `value`, `vintage`, `evidence_kind`.
- Never merge into observed job KPI numerators without explicit labeling (ADR-001).

## Field map → reference facts (not RawJob)
| Source | FMI field | Notes |
|--------|-----------|-------|
| Agency series / survey row | `reference_metric` | Numeric or categorical benchmark |
| Publication date | `vintage` | Survey year or release date |
| Geography | `geo` | ISO3166 / agency code |

## Geo / compliance
- Global.
- Lawful download/API only; no paywall or ToS-prohibited scraping (ADR-003).

## Gaps / next step
- Indicator catalog is huge — allowlist indicators.
