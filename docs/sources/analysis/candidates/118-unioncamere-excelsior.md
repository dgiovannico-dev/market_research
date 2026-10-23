# Unioncamere Excelsior (catalog_id=118)

| Field | Value |
|-------|-------|
| Analysis | DOCUMENTED |
| Role | `reference_not_jobs` — category **E**; not `RawJob` ingest |
| verification_status | UNDER_REVIEW |
| access_mode | portal |
| connector_key | — |

## Official / docs
- Official: https://excelsior.unioncamere.net/
- Docs: https://excelsior.unioncamere.net/
- Catalog note: Official statistics — import via datasets/API; do not mix incomparable series. Not wired as job connector.

## Access path (reference import)
- Preferred: Unioncamere Excelsior portal + reports.
- excelsior.unioncamere.net publications.
- Auth: per provider (portal).
- Series / tables: Professional profiles demand/supply, hiring intentions (IT).

## FMI use (context KPIs — not RawJob)
- IT occupation demand reference (employer survey based).
- Store: `provider`, `series_id`, `geo`, `time`, `value`, `vintage`, `evidence_kind`.
- Never merge into observed job KPI numerators without explicit labeling (ADR-001).

## Field map → reference facts (not RawJob)
| Source | FMI field | Notes |
|--------|-----------|-------|
| Agency series / survey row | `reference_metric` | Numeric or categorical benchmark |
| Publication date | `vintage` | Survey year or release date |
| Geography | `geo` | ISO3166 / agency code |

## Geo / compliance
- Italy.
- Lawful download/API only; no paywall or ToS-prohibited scraping (ADR-003).

## Gaps / next step
- Acquire licensed bulk if API absent.
