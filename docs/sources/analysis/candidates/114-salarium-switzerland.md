# Salarium Switzerland (catalog_id=114)

| Field | Value |
|-------|-------|
| Analysis | DOCUMENTED |
| Role | `reference_not_jobs` — category **E**; not `RawJob` ingest |
| verification_status | UNDER_REVIEW |
| access_mode | portal |
| connector_key | — |

## Official / docs
- Official: https://www.salarium.bfs.admin.ch/
- Docs: https://www.salarium.bfs.admin.ch/
- Catalog note: Official statistics — import via datasets/API; do not mix incomparable series. Not wired as job connector.

## Access path (reference import)
- Preferred: Salarium.ch interactive tables (BFS earnings structure).
- Portal queries; export where offered.
- Auth: per provider (portal).
- Series / tables: Median/mean earnings by occupation, sector, age, sex.

## FMI use (context KPIs — not RawJob)
- CH salary benchmark context (official); not contractor day rates.
- Store: `provider`, `series_id`, `geo`, `time`, `value`, `vintage`, `evidence_kind`.
- Never merge into observed job KPI numerators without explicit labeling (ADR-001).

## Field map → reference facts (not RawJob)
| Source | FMI field | Notes |
|--------|-----------|-------|
| Agency series / survey row | `reference_metric` | Numeric or categorical benchmark |
| Publication date | `vintage` | Survey year or release date |
| Geography | `geo` | ISO3166 / agency code |

## Geo / compliance
- Switzerland.
- Lawful download/API only; no paywall or ToS-prohibited scraping (ADR-003).

## Gaps / next step
- Manual or semi-automated export pipeline.
