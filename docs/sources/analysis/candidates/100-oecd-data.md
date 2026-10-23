# OECD Data (catalog_id=100)

| Field | Value |
|-------|-------|
| Analysis | DOCUMENTED |
| Role | `reference_not_jobs` — category **E**; not `RawJob` ingest |
| verification_status | UNDER_REVIEW |
| access_mode | open_data |
| connector_key | — |

## Official / docs
- Official: https://data.oecd.org/
- Docs: https://data.oecd.org/
- Catalog note: Official statistics — import via datasets/API; do not mix incomparable series. Not wired as job connector.

## Access path (reference import)
- Preferred: OECD.Stat SDMX REST (`data-api.oecd.org`).
- `GET https://data-api.oecd.org/…` (dataset-specific path).
- Auth: per provider (open_data).
- Series / tables: Employment/unemployment (`STLABOUR`), earnings (`AV_AN_WAGE`), ICT employment.

## FMI use (context KPIs — not RawJob)
- Macro labour context for country lens; store series id + vintage.
- Store: `provider`, `series_id`, `geo`, `time`, `value`, `vintage`, `evidence_kind`.
- Never merge into observed job KPI numerators without explicit labeling (ADR-001).

## Field map → reference facts (not RawJob)
| Source | FMI field | Notes |
|--------|-----------|-------|
| Agency series / survey row | `reference_metric` | Numeric or categorical benchmark |
| Publication date | `vintage` | Survey year or release date |
| Geography | `geo` | ISO3166 / agency code |

## Geo / compliance
- OECD members + partners.
- Lawful download/API only; no paywall or ToS-prohibited scraping (ADR-003).

## Gaps / next step
- Pick 3–5 stable series ids; rate-limit friendly caching.
