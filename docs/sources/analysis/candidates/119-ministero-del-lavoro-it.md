# Ministero del Lavoro IT (catalog_id=119)

| Field | Value |
|-------|-------|
| Analysis | DOCUMENTED |
| Role | `reference_not_jobs` — category **E**; not `RawJob` ingest |
| verification_status | UNDER_REVIEW |
| access_mode | portal |
| connector_key | — |

## Official / docs
- Official: https://www.lavoro.gov.it/
- Docs: https://www.lavoro.gov.it/
- Catalog note: Official statistics — import via datasets/API; do not mix incomparable series. Not wired as job connector.

## Access path (reference import)
- Preferred: Ministero del Lavoro open data / MLPS publications.
- dati.lavoro.gov.it / institutional reports.
- Auth: per provider (portal).
- Series / tables: Labour market program stats, contractual forms, sector bulletins.

## FMI use (context KPIs — not RawJob)
- IT policy and labour market context footnotes.
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
- Identify stable open-data endpoints vs HTML-only pages.
