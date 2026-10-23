# Hays Salary Guides (catalog_id=140)

| Field | Value |
|-------|-------|
| Analysis | DOCUMENTED |
| Role | `survey_salary_reference` — category **F**; not `RawJob` ingest |
| verification_status | UNDER_REVIEW |
| access_mode | report_or_dataset |
| connector_key | — |

## Official / docs
- Official: https://www.hays.com/salary-guide
- Docs: https://www.hays.com/salary-guide
- Catalog note: Survey/report — use lawful download/import; do not scrape paywalled pages. Not a live job connector.

## Access path (reference import)
- Preferred: Hays annual salary guide PDFs (free download, marketing).
- hays.com/salary-guide regional PDFs.
- Auth: per provider (report_or_dataset).
- Series / tables: Recruiter survey salary ranges by role/region.

## FMI use (context KPIs — not RawJob)
- Agency benchmark narrative; manual CSV extraction if permitted.
- Store: `provider`, `series_id`, `geo`, `time`, `value`, `vintage`, `evidence_kind`.
- Never merge into observed job KPI numerators without explicit labeling (ADR-001).

## Field map → reference facts (not RawJob)
| Source | FMI field | Notes |
|--------|-----------|-------|
| Agency series / survey row | `reference_metric` | Numeric or categorical benchmark |
| Publication date | `vintage` | Survey year or release date |
| Geography | `geo` | ISO3166 / agency code |

## Geo / compliance
- Multi-country (guide per market).
- Lawful download/API only; no paywall or ToS-prohibited scraping (ADR-003).

## Gaps / next step
- PDF parsing policy; cite Hays as source.
