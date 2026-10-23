# Netherlands (NL) job ingest — coverage note

**Date:** 2026-10-21  
**Policy:** [ADR-003](../decisions/ADR-003-authorized-connectors-only.md) — no Werk.nl HTML scrape or undocumented BFF harvest.

## Official PES (UWV / Werk.nl)

| Item | Detail |
|------|--------|
| Vacancy search | https://www.werk.nl/werkzoekenden/vacatures/ |
| Open data | [UWV Open Match](https://data.overheid.nl/en/dataset/uwv-open-match-data) — **aggregated** vacancy/CV counts by occupation × 4-digit postcode (CC-BY), not individual listings |
| Listing API | **None.** [data.overheid.nl request #2258](https://data.overheid.nl/community/datarequest/vacatures-werk-nl): UWV confirmed no API and no near-term plan; scraping mentioned by UWV is **not** an authorized connector path for FMI |
| Priority | **P2** for aggregates; listings **BLOCKED** until an official listing API exists |

## Authorized free listing paths in repo

| Connector | Role | Caveat |
|-----------|------|--------|
| `findmethatdamjob` | Documented public API ([docs](https://findmethatdamjob.nl/docs/api/)); careers-page aggregator, NL-wide via `location=amsterdam` | Not PES; tech-heavy Amsterdam ecosystem bias; respect employer ToS on republish |
| `devitjobs` | Free `jobsLight` on `devitjobs.nl` host (multi-host collector) | IT board; smaller NL slice than UK |
| `adzuna` | Documented REST when `ADZUNA_COUNTRIES` includes `nl` | **NEEDS_CREDENTIALS**; commercial licence for ongoing aggregation |

## Partner / not implemented

| Source | Access |
|--------|--------|
| [Nationale Vacaturebank](https://www.nationalevacaturebank.nl/) | No verified public job API this pass — catalog `UNDER_REVIEW` |
| [VDAB-style NL boards](https://www.techleap.nl/) (Techleap job board) | No documented public API |
| Third-party Werk.nl wrappers (Parse, Apify, etc.) | Paid scrape proxies — **REJECTED** under ADR-003 |

## Operator

Enable `findmethatdamjob` via catalog seed (`ACTIVE`, no key). Optional: `ADZUNA_*` with `nl` for broader national mix. Do **not** enable Werk.nl scrapers.
