# Stack Overflow Developer Survey (catalog_id=131)

| Field | Value |
|-------|-------|
| Analysis | DOCUMENTED |
| Role | `survey_salary_reference` — category **F**; not `RawJob` ingest |
| verification_status | UNDER_REVIEW |
| access_mode | report_or_dataset |
| connector_key | — |

## Official / docs
- Official: https://survey.stackoverflow.co/
- Docs: https://survey.stackoverflow.co/
- Catalog note: Survey/report — use lawful download/import; do not scrape paywalled pages. Not a live job connector.

## Access path (reference import)
- Preferred: Annual public CSV release on survey.stackoverflow.co.
- Download links per year (developer survey results).
- Auth: per provider (report_or_dataset).
- Series / tables: Dev salaries, stack, remote work (self-reported sample).

## FMI use (context KPIs — not RawJob)
- Tech salary/skill sentiment context — label as survey not official.
- Store: `provider`, `series_id`, `geo`, `time`, `value`, `vintage`, `evidence_kind`.
- Never merge into observed job KPI numerators without explicit labeling (ADR-001).

## Field map → reference facts (not RawJob)
| Source | FMI field | Notes |
|--------|-----------|-------|
| Agency series / survey row | `reference_metric` | Numeric or categorical benchmark |
| Publication date | `vintage` | Survey year or release date |
| Geography | `geo` | ISO3166 / agency code |

## Geo / compliance
- Global (biased sample).
- Lawful download/API only; no paywall or ToS-prohibited scraping (ADR-003).

## Gaps / next step
- Manual import via `manual_import`; no scraping site UI.
