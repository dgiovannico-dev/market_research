# US O*NET (catalog_id=107)

| Field | Value |
|-------|-------|
| Analysis | DOCUMENTED |
| Role | `reference_not_jobs` — category **E**; not `RawJob` ingest |
| verification_status | UNDER_REVIEW |
| access_mode | api_key |
| connector_key | — |

## Official / docs
- Official: https://www.onetonline.org/
- Docs: https://www.onetonline.org/
- Catalog note: Official statistics — import via datasets/API; do not mix incomparable series. Not wired as job connector.

## Access path (reference import)
- Preferred: O*NET public site + separate Web Services (catalog 150, keyed).
- Browse/download at onetonline.org; API via services.onetcenter.org.
- Auth: per provider (api_key).
- Series / tables: Occupation profiles: skills, tasks, wages (US SOC).

## FMI use (context KPIs — not RawJob)
- Taxonomy bridge SOC↔skills for US roles; reference profiles not postings.
- Store: `provider`, `series_id`, `geo`, `time`, `value`, `vintage`, `evidence_kind`.
- Never merge into observed job KPI numerators without explicit labeling (ADR-001).

## Field map → reference facts (not RawJob)
| Source | FMI field | Notes |
|--------|-----------|-------|
| Agency series / survey row | `reference_metric` | Numeric or categorical benchmark |
| Publication date | `vintage` | Survey year or release date |
| Geography | `geo` | ISO3166 / agency code |

## Geo / compliance
- US SOC system.
- Lawful download/API only; no paywall or ToS-prohibited scraping (ADR-003).

## Gaps / next step
- Use Web Services for machine access; static CSV for offline allowlist.
