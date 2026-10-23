# JetBrains Developer Ecosystem (catalog_id=132)

| Field | Value |
|-------|-------|
| Analysis | DOCUMENTED |
| Role | `survey_salary_reference` — category **F**; not `RawJob` ingest |
| verification_status | UNDER_REVIEW |
| access_mode | report_or_dataset |
| connector_key | — |

## Official / docs
- Official: https://www.jetbrains.com/lp/devecosystem/
- Docs: https://www.jetbrains.com/lp/devecosystem/
- Catalog note: Survey/report — use lawful download/import; do not scrape paywalled pages. Not a live job connector.

## Access path (reference import)
- Preferred: JetBrains DevEco public datasets / reports.
- devecosystem.jetbrains.com raw data downloads.
- Auth: per provider (report_or_dataset).
- Series / tables: Language/tool adoption, employment status of developers.

## FMI use (context KPIs — not RawJob)
- Ecosystem trend context for tech briefs.
- Store: `provider`, `series_id`, `geo`, `time`, `value`, `vintage`, `evidence_kind`.
- Never merge into observed job KPI numerators without explicit labeling (ADR-001).

## Field map → reference facts (not RawJob)
| Source | FMI field | Notes |
|--------|-----------|-------|
| Agency series / survey row | `reference_metric` | Numeric or categorical benchmark |
| Publication date | `vintage` | Survey year or release date |
| Geography | `geo` | ISO3166 / agency code |

## Geo / compliance
- Global survey sample.
- Lawful download/API only; no paywall or ToS-prohibited scraping (ADR-003).

## Gaps / next step
- Year-over-year schema drift.
