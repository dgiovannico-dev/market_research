# Australian Labour Market Insights (catalog_id=111)

| Field | Value |
|-------|-------|
| Analysis | DOCUMENTED |
| Role | `reference_not_jobs` — category **E**; not `RawJob` ingest |
| verification_status | UNDER_REVIEW |
| access_mode | portal |
| connector_key | — |

## Official / docs
- Official: https://labourmarketinsights.gov.au/
- Docs: https://labourmarketinsights.gov.au/
- Catalog note: Official statistics — import via datasets/API; do not mix incomparable series. Not wired as job connector.

## Access path (reference import)
- Preferred: Australian Labour Market Insights portal (derived from ABS/JSA).
- Portal exports / embedded charts; no job ingest API.
- Auth: per provider (portal).
- Series / tables: Occupation outlook, employment projections, regional summaries.

## FMI use (context KPIs — not RawJob)
- Briefing context for AU occupation demand (official narrative).
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
- Prefer ABS API for time series; LMI for occupation copy.
