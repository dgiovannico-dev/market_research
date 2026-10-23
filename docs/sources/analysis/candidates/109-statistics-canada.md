# Statistics Canada (catalog_id=109)

| Field | Value |
|-------|-------|
| Analysis | DOCUMENTED |
| Role | `reference_not_jobs` — category **E**; not `RawJob` ingest |
| verification_status | UNDER_REVIEW |
| access_mode | open_data |
| connector_key | — |

## Official / docs
- Official: https://www.statcan.gc.ca/
- Docs: https://www.statcan.gc.ca/
- Catalog note: Official statistics — import via datasets/API; do not mix incomparable series. Not wired as job connector.

## Access path (reference import)
- Preferred: Statistics Canada Web Data Service (WDS) / open data.
- StatCan WDS tables by table id.
- Auth: per provider (open_data).
- Series / tables: Labour Force Survey tables (unemployment, employment by industry).

## FMI use (context KPIs — not RawJob)
- CA national context KPIs.
- Store: `provider`, `series_id`, `geo`, `time`, `value`, `vintage`, `evidence_kind`.
- Never merge into observed job KPI numerators without explicit labeling (ADR-001).

## Field map → reference facts (not RawJob)
| Source | FMI field | Notes |
|--------|-----------|-------|
| Agency series / survey row | `reference_metric` | Numeric or categorical benchmark |
| Publication date | `vintage` | Survey year or release date |
| Geography | `geo` | ISO3166 / agency code |

## Geo / compliance
- Canada.
- Lawful download/API only; no paywall or ToS-prohibited scraping (ADR-003).

## Gaps / next step
- Table id allowlist; English/French labels.
