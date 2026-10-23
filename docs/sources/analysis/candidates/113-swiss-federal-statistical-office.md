# Swiss Federal Statistical Office (catalog_id=113)

| Field | Value |
|-------|-------|
| Analysis | DOCUMENTED |
| Role | `reference_not_jobs` — category **E**; not `RawJob` ingest |
| verification_status | UNDER_REVIEW |
| access_mode | open_data |
| connector_key | — |

## Official / docs
- Official: https://www.bfs.admin.ch/
- Docs: https://www.bfs.admin.ch/
- Catalog note: Official statistics — import via datasets/API; do not mix incomparable series. Not wired as job connector.

## Access path (reference import)
- Preferred: BFS open data portal (REST/CSV).
- opendata.swiss / BFS PxWeb-API.
- Auth: per provider (open_data).
- Series / tables: SLFS unemployment, employment, wages (Swiss official).

## FMI use (context KPIs — not RawJob)
- CH labour market context KPIs.
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
- Language DE/FR/IT metadata handling.
