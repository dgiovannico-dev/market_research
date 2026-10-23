# US Census Bureau (catalog_id=106)

| Field | Value |
|-------|-------|
| Analysis | DOCUMENTED |
| Role | `reference_not_jobs` — category **E**; not `RawJob` ingest |
| verification_status | UNDER_REVIEW |
| access_mode | api_key |
| connector_key | — |

## Official / docs
- Official: https://www.census.gov/data.html
- Docs: https://www.census.gov/data.html
- Catalog note: Official statistics — import via datasets/API; do not mix incomparable series. Not wired as job connector.

## Access path (reference import)
- Preferred: Census Bureau API (key required).
- `https://api.census.gov/data/{year}/…`
- Auth: per provider (api_key).
- Series / tables: American Community Survey occupation/industry employment counts.

## FMI use (context KPIs — not RawJob)
- US demographic/occupation structure context — not vacancy flow.
- Store: `provider`, `series_id`, `geo`, `time`, `value`, `vintage`, `evidence_kind`.
- Never merge into observed job KPI numerators without explicit labeling (ADR-001).

## Field map → reference facts (not RawJob)
| Source | FMI field | Notes |
|--------|-----------|-------|
| Agency series / survey row | `reference_metric` | Numeric or categorical benchmark |
| Publication date | `vintage` | Survey year or release date |
| Geography | `geo` | ISO3166 / agency code |

## Geo / compliance
- US.
- Lawful download/API only; no paywall or ToS-prohibited scraping (ADR-003).

## Gaps / next step
- ACS lag; document vintage in UI.
