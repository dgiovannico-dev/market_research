# Geographic sources — P0 shortlist

**Date:** 2026-10-21  
**Inputs:** [GEO_COVERAGE_GAP.md](GEO_COVERAGE_GAP.md), [GEO_RESEARCH_IT_CH_LU_DE.md](GEO_RESEARCH_IT_CH_LU_DE.md), [GEO_RESEARCH_EU.md](GEO_RESEARCH_EU.md), [GEO_RESEARCH_UK_US_AU.md](GEO_RESEARCH_UK_US_AU.md), [GEO_RESEARCH_ACCESS_PATHS.md](GEO_RESEARCH_ACCESS_PATHS.md).  
**Policy:** Authorized API/RSS/open data only ([ADR-003](../decisions/ADR-003-authorized-connectors-only.md)). No LinkedIn/Indeed/EURES SPA scrape.

P0 collector/UI code for the wave below is **in repo** (see [Shipped in repo](#shipped-in-repo-2026-10-21)). Remaining gate: **keys / partner / legal** before treating keyed sources as ACTIVE production paths.

## Shipped in repo (2026-10-21)

Verified against `backend/app/collectors/registry.py` and related collectors/UI:

- [x] **Adzuna** multi-country via `ADZUNA_COUNTRIES` (fallback `ADZUNA_COUNTRY` / `gb`) — registered `adzuna`; still needs `ADZUNA_APP_ID` / `ADZUNA_APP_KEY`
- [x] **JobUp** IT query fan-out + pagination (up to 3 pages / variants) — already ACTIVE path when query present
- [x] **USAJOBS** optional `USAJOBS_JOB_CATEGORY_CODE` → `JobCategoryCode` (e.g. `2210`) — registered; keyed
- [x] **France Travail** Offres v2 with IT ROME codes (`M1805`/`M1802`/`M1806`) + up to 2 pages — registered; OAuth keys
- [x] **Tecnoempleo** / **Le Forem** / **MPSV** — collectors + catalog `ACTIVE` (ids 24 / 35 / 195); seed → `Source.enabled=true`
- [x] **Findwork** scaffold (`findwork` + `FINDWORK_API_KEY`) — catalog `NEEDS_CREDENTIALS` id 196; disabled until key + promote
- [x] **Careerjet** Partner API v4 scaffold (`careerjet` + `CAREERJET_API_KEY` / `CAREERJET_USER_IP`) — locales IT/DE/CH/LU; `NEEDS_CREDENTIALS`
- [x] **InfoJobs** Italy developer API scaffold (`infojobs` + client id/secret) — `NEEDS_CREDENTIALS`; partner terms before ACTIVE
- [x] **Jobs** list pagination UI (`JobsPagination` / `JobsListDashboard`)
- [x] **Atlas UX** — [SPEC-ux-shell.md](../specs/SPEC-ux-shell.md) (four nav zones, design tokens, chrome plan)
- [x] **Live insert evidence (local compose):** tecnoempleo 80 / le_forem 180 / mpsv 289 / jobup 57 (see VALIDATION_REPORT)

## Critical gaps today

| Region | Gap |
|--------|-----|
| **IT** | InfoJobs.it **closed** (API = Spain — remap geo). No PES vacancy API. Path: ATS IT tenants + Excelsior/Eurostat OJA; Adzuna/Careerjet with licence. See [IT_CH_LU_COVERAGE.md](IT_CH_LU_COVERAGE.md) |
| **LU** | Thin `devglobaljobs`; ADEM CC0 open data documented — wire ingest; ATS `country=lu` tenants. EURES/jobs.lu = partner only |
| **DE** | Arbeitnow only; `bundesagentur` credential + ToS gate |
| **CH** | JobUp ACTIVE but JobCloud ToS/`robots` conflict — prefer affiliate; Adzuna `ch` + Careerjet + ATS; Job-Room needs SECO consent |
| **NL** | No official PES listing API (UWV/Werk.nl); `findmethatdamjob` + `devitjobs.nl` partial; Adzuna `nl` when keyed — [NL_JOBS_COVERAGE.md](NL_JOBS_COVERAGE.md) |
| **AU** | `viewjobs` ACTIVE (free MCP); Adzuna when keyed |
| **ES** | Tecnoempleo RSS ACTIVE; InfoJobs keyed |
| **FR / US** | Collectors registered + enriched; ACTIVE only after keys (`france_travail`, `usajobs`; Findwork scaffold) |

## Recommended P0 wave (ordered)

| # | Action | Geo | Access | Why / caveat |
|---|--------|-----|--------|--------------|
| 1 | Activate **Adzuna** multi-country (`it`, `de`, `ch`, `gb`, `us`, `au`, + EU where keyed) | IT/DE/CH/UK/US/AU | Self-serve keys (multi-country **shipped**) | Fastest legal multi-geo lift. Eval tier OK; **ongoing commercial aggregation needs written Adzuna licence** after org trial ([ACCESS_PATHS](GEO_RESEARCH_ACCESS_PATHS.md)) |
| 2 | Deepen **JobUp** IT queries; keep **Arbeitnow** | CH / DE | Already ACTIVE | Fan-out/pagination **shipped**; fill DACH without new vendors |
| 3 | Activate **USAJOBS** (IT category `2210` / software keywords) | US | Keys | `USAJOBS_JOB_CATEGORY_CODE` **shipped**; official federal IT |
| 4 | Activate **France Travail** Offres v2 | FR | OAuth keys | IT ROME + 2-page fetch **shipped** |
| 5 | Optional **Reed JSON** (keyed) alongside RSS | UK | Optional key | Richer UK contract/salary than RSS |
| 6 | Open-data EU: **MPSV CZ**, **Le Forem BE**, **Tecnoempleo RSS** ES | CZ/BE/ES | Open / RSS | Catalog **ACTIVE** + seed-enabled (no keys). Tecnoempleo = RSS only, not Empléate Solr. |

## P1 (partner / quota / legal gate — after P0)

| Action | Geo | Note |
|--------|-----|------|
| **InfoJobs IT** developer API | IT | Scaffold shipped; partner signup + keys + promote after inserts |
| **jobs.lu JobWS** + optional **ADEM** CC0 | LU | Partner/keyed SOAP — not self-serve ([ACCESS_PATHS](GEO_RESEARCH_ACCESS_PATHS.md)) |
| **Jooble** AU/US (+ other countries) | multi | Self-serve but **500 lifetime requests/key** — probe only unless quota raised |
| **Findwork.dev** | US/remote | Self-serve token; catalog `NEEDS_CREDENTIALS` (id 196). Set `FINDWORK_API_KEY`, restart/seed, promote after inserts ([UK/US/AU](GEO_RESEARCH_UK_US_AU.md)) |
| **Careerjet** Partner API v4 | IT/DE/CH/LU | Scaffold shipped; publisher key + `CAREERJET_USER_IP`; optional `CAREERJET_LOCALES` |
| **BA Jobsuche** promote to ACTIVE | DE | Public key exists; **ToS appear to forbid Datensammlung** — legal/BA OK first |

## Explicitly deferred

| Item | Reason |
|------|--------|
| EURES public/SPA | Partner/NCO only; unofficial SPA forbidden |
| StepStone / SEEK / Dice / JobCloud / Job-Room read | Partner or write-only |
| CWJobs / ACT RSS | Documented but 403/Cloudflare from current egress |
| Ministero Lavoro SPARQL | Ops-fragile |

## Enable free geo collectors (Sources rows)

Restart API (or trigger seed) so `_sync_catalog_sources` upserts from `data/sources/catalog.json`: `tecnoempleo` / `le_forem` / `mpsv` → `enabled=true` when `ACTIVE` and key ∈ `COLLECTORS`. Then `POST /api/v1/sources/{id}/run`. Credentialed scaffolds (`findwork`, `careerjet`, `infojobs`, …) stay **disabled** until matching env vars + seed + `promote_source_active.py` after a live insert run ([CREDENTIALED_CONNECTORS.md](CREDENTIALED_CONNECTORS.md)).

## Approval checkpoint

**Code for P0 items 1–4 and 6 is in repo** (plus Findwork scaffold / Jobs UI / Atlas UX). Still approve before production reliance:

1. **Keys:** Adzuna (`ADZUNA_APP_ID`/`ADZUNA_APP_KEY` + `ADZUNA_COUNTRIES`), USAJOBS, France Travail OAuth, optional Findwork / Reed JSON.
2. **Licence / partner:** Adzuna ongoing commercial use; do **not** code P1 (InfoJobs / jobs.lu / Jooble expand / BA ACTIVE) until partner/legal path is clear.
3. **Open-data slice:** confirm Tecnoempleo / Le Forem / MPSV ops cadence after first live runs.
