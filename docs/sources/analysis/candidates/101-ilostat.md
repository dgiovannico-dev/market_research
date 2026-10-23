# ILOSTAT (catalog_id=101)

| Field | Value |
|-------|-------|
| Analysis | DOCUMENTED |
| Role | `reference_not_jobs` — category **E**; not `RawJob` ingest |
| verification_status | UNDER_REVIEW |
| access_mode | open_data |
| connector_key | — |

## Official / docs
- Official: https://ilostat.ilo.org/
- Docs: https://ilostat.ilo.org/
- Catalog note: Official statistics — import via datasets/API; do not mix incomparable series. Not wired as job connector.

## Access path (reference import)
- Preferred: ILOSTAT bulk/API (SDMX and CSV exports).
- ILO API gateway documented at ilostat.ilo.org/data/
- Auth: per provider (open_data).
- Series / tables: Unemployment, labour force, wages (`SDG_08`, `EMP`, `UNE`).

## FMI use (context KPIs — not RawJob)
- Global baseline when Eurostat/OECD missing; ILO methodology footnotes required.
- Store: `provider`, `series_id`, `geo`, `time`, `value`, `vintage`, `evidence_kind`.
- Never merge into observed job KPI numerators without explicit labeling (ADR-001).

## Field map → reference facts (not RawJob)
| Source | FMI field | Notes |
|--------|-----------|-------|
| Agency series / survey row | `reference_metric` | Numeric or categorical benchmark |
| Publication date | `vintage` | Survey year or release date |
| Geography | `geo` | ISO3166 / agency code |

## Geo / compliance
- Global ISO3.
- Lawful download/API only; no paywall or ToS-prohibited scraping (ADR-003).

## Gaps / next step
- Map ILO country codes to ISO3166 once in import layer.
