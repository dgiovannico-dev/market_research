# UK ONS (catalog_id=122)

| Field | Value |
|-------|-------|
| Analysis | DOCUMENTED |
| Role | `reference_not_jobs` — category **E**; not `RawJob` ingest |
| verification_status | UNDER_REVIEW |
| access_mode | open_data |
| connector_key | — |

## Official / docs
- Official: https://www.ons.gov.uk/
- Docs: https://www.ons.gov.uk/
- Catalog note: Official statistics — import via datasets/API; do not mix incomparable series. Not wired as job connector.

## Access path (reference import)
- Preferred: ONS Time Series API / Beta API.
- `https://api.ons.gov.uk/timeseries/{id}/data`
- Auth: per provider (open_data).
- Series / tables: MGSX, LF24 (unemployment), EMP (employment), ASHE earnings.

## FMI use (context KPIs — not RawJob)
- UK national KPI bands; ASHE for earnings context.
- Store: `provider`, `series_id`, `geo`, `time`, `value`, `vintage`, `evidence_kind`.
- Never merge into observed job KPI numerators without explicit labeling (ADR-001).

## Field map → reference facts (not RawJob)
| Source | FMI field | Notes |
|--------|-----------|-------|
| Agency series / survey row | `reference_metric` | Numeric or categorical benchmark |
| Publication date | `vintage` | Survey year or release date |
| Geography | `geo` | ISO3166 / agency code |

## Geo / compliance
- UK.
- Lawful download/API only; no paywall or ToS-prohibited scraping (ADR-003).

## Gaps / next step
- ONS dataset migration — pin series ids.
