# GitHub Octoverse (catalog_id=133)

| Field | Value |
|-------|-------|
| Analysis | DOCUMENTED |
| Role | `survey_salary_reference` — category **F**; not `RawJob` ingest |
| verification_status | UNDER_REVIEW |
| access_mode | report_or_dataset |
| connector_key | — |

## Official / docs
- Official: https://github.blog/news-insights/octoverse/
- Docs: https://github.blog/news-insights/octoverse/
- Catalog note: Survey/report — use lawful download/import; do not scrape paywalled pages. Not a live job connector.

## Access path (reference import)
- Preferred: GitHub Octoverse annual report (PDF/blog); optional GitHub REST for public metrics.
- Report assets; `api.github.com` for repo stats (not salaries).
- Auth: per provider (report_or_dataset).
- Series / tables: Language growth, OSS activity (narrative + charts).

## FMI use (context KPIs — not RawJob)
- Supply-side tech trend context only.
- Store: `provider`, `series_id`, `geo`, `time`, `value`, `vintage`, `evidence_kind`.
- Never merge into observed job KPI numerators without explicit labeling (ADR-001).

## Field map → reference facts (not RawJob)
| Source | FMI field | Notes |
|--------|-----------|-------|
| Agency series / survey row | `reference_metric` | Numeric or categorical benchmark |
| Publication date | `vintage` | Survey year or release date |
| Geography | `geo` | ISO3166 / agency code |

## Geo / compliance
- Global.
- Lawful download/API only; no paywall or ToS-prohibited scraping (ADR-003).

## Gaps / next step
- No occupation wages — do not conflate with compensation KPIs.
