# Levels.fyi (catalog_id=136)

| Field | Value |
|-------|-------|
| Analysis | DOCUMENTED |
| Role | `survey_salary_reference` — category **F**; not `RawJob` ingest |
| verification_status | UNDER_REVIEW |
| access_mode | report_or_dataset |
| connector_key | — |

## Official / docs
- Official: https://www.levels.fyi/
- Docs: https://www.levels.fyi/
- Catalog note: Survey/report — use lawful download/import; do not scrape paywalled pages. Not a live job connector.

## Access path (reference import)
- Preferred: Levels.fyi public aggregates; no authorized bulk API for scraping.
- User-contributed comp tables on site; partner/data deals only.
- Auth: per provider (report_or_dataset).
- Series / tables: Tech total comp by company/level (crowd reported).

## FMI use (context KPIs — not RawJob)
- Optional manual benchmark import; **BLOCKED** for automated scrape.
- Store: `provider`, `series_id`, `geo`, `time`, `value`, `vintage`, `evidence_kind`.
- Never merge into observed job KPI numerators without explicit labeling (ADR-001).

## Field map → reference facts (not RawJob)
| Source | FMI field | Notes |
|--------|-----------|-------|
| Agency series / survey row | `reference_metric` | Numeric or categorical benchmark |
| Publication date | `vintage` | Survey year or release date |
| Geography | `geo` | ISO3166 / agency code |

## Geo / compliance
- US-heavy tech hubs.
- Lawful download/API only; no paywall or ToS-prohibited scraping (ADR-003).

## Gaps / next step
- Partner API or licensed export only (ADR-003).
