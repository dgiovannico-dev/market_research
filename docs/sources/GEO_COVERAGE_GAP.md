# Geographic coverage gap matrix

Evidence-only snapshot of **registered collectors** in `backend/app/collectors/registry.py` vs target regions. Does **not** invent new collectors. Cross-check: [VALIDATION_REPORT.md](VALIDATION_REPORT.md), [CREDENTIALED_CONNECTORS.md](CREDENTIALED_CONNECTORS.md), catalog `data/sources/catalog.json`. Broader gaps: [COVERAGE_GAPS.md](COVERAGE_GAPS.md).

**As of:** 2026-10-21 (docs + registry code).

| Status used here | Meaning |
|------------------|---------|
| ACTIVE | Catalog/validation: connector live + verified (see VALIDATION_REPORT) |
| NEEDS_CREDENTIALS | In registry as scaffold; catalog stays NEEDS_CREDENTIALS until keyed live ingest + promote |
| Partial | No dedicated geo collector; only remote/EU/ATS bleed |

---

## 1. Full collector inventory (registry)

Geo affinity from `COLLECTOR_GEO` when present; otherwise from module docstring / VALIDATION_REPORT / COVERAGE_GAPS. Modes from each collector’s `collection_mode`.

| Key | Mode | Geo / affinity | Doc status |
|-----|------|----------------|------------|
| `remotive` | dump | Global remote | ACTIVE |
| `arbeitnow` | dump | EU, DE-heavy (not in `COLLECTOR_GEO`) | ACTIVE |
| `remoteok` | dump | Global remote | ACTIVE |
| `working_nomads` | dump | Global remote | ACTIVE |
| `weworkremotely` | feed | Global remote | ACTIVE |
| `themuse` | dump | Global (employer API; US-leaning corpus) | ACTIVE |
| `jobicy` | dump | Global remote | ACTIVE |
| `himalayas` | dump | Global remote | ACTIVE |
| `hn_whoishiring` | feed | Global (HN hiring threads) | ACTIVE |
| `devitjobs` | dump | `GB`/`UK`/`EU` | ACTIVE |
| `nofluffjobs` | dump | `PL`,`HU`,`CZ`,`SK`,`UA` | ACTIVE |
| `getonbrd` | dump | `CL`,`MX`,`AR`,`CO`,`PE`,`BR` | ACTIVE |
| `mycareersfuture` | search | `SG` | ACTIVE |
| `jobup` | search | `CH` | ACTIVE |
| `nav_arbeidsplassen` | search | `NO` | ACTIVE |
| `landing_jobs` | dump | `PT`,`EU` | ACTIVE |
| `okemprego` | dump | `PT` (optional `BR`,`AO`) | ACTIVE |
| `jobbank_ca` | dump | `CA` | ACTIVE |
| `devglobaljobs` | dump | `LU`,`BG` (configurable) | ACTIVE |
| `viewjobs` | search | `AU` | ACTIVE |
| `kalibrr` | search | `PH`,`ID` | ACTIVE |
| `dou_ua` | feed | `UA` | ACTIVE |
| `authentic_jobs` | feed | Design/dev remote (global) | ACTIVE |
| `wantedly` | search | `JP` | ACTIVE |
| `duunitori` | search | `FI` | ACTIVE |
| `jobindex` | feed | `DK` | ACTIVE |
| `wanted` | search | `KR` | ACTIVE |
| `instahyre` | search | `IN` | ACTIVE |
| `hasjob` | dump | `IN` | ACTIVE |
| `helloworld_rs` | feed | `RS` | ACTIVE |
| `posao_hr` | feed | `HR` | ACTIVE |
| `jobweb_kenya` | feed | `KE` | ACTIVE |
| `tecnoempleo` | feed | `ES` | ACTIVE |
| `le_forem` | dump | `BE` | ACTIVE |
| `mpsv` | dump | `CZ` | ACTIVE |
| `findmethatdamjob` | search | `NL` | ACTIVE |
| `greenhouse` | dump | ATS tenants (company list, not country) | ACTIVE |
| `lever` | dump | ATS tenants | ACTIVE |
| `ashby` | dump | ATS tenants | ACTIVE |
| `smartrecruiters` | dump | ATS tenants | ACTIVE |
| `arbetsformedlingen` | search | `SE` | ACTIVE |
| `reed` | feed | `GB`/`UK` (optional JSON API key) | ACTIVE |
| `adzuna` | search | `GB`/`UK` default (`ADZUNA_COUNTRY`, default `gb`) | NEEDS_CREDENTIALS |
| `usajobs` | search | `US` | NEEDS_CREDENTIALS |
| `france_travail` | search | `FR` | NEEDS_CREDENTIALS |
| `bundesagentur` | search | `DE` | NEEDS_CREDENTIALS |
| `jooble` | search | Multi-geo via `JOOBLE_LOCATION` (not in `COLLECTOR_GEO`) | NEEDS_CREDENTIALS |
| `findwork` | search | `US` | NEEDS_CREDENTIALS |
| `careerjet` | search | `IT`, `DE`, `CH`, `LU` (`CAREERJET_LOCALES`) | NEEDS_CREDENTIALS |
| `infojobs` | search | `IT` (optional `INFOJOBS_COUNTRY`) | NEEDS_CREDENTIALS |

**Counts:** 49 registry collectors — **41** public/ATS path (catalog ACTIVE when wired) + **8** credentialed scaffolds (`CREDENTIALED_SCAFFOLDS`: `adzuna`, `usajobs`, `france_travail`, `bundesagentur`, `jooble`, `findwork`, `careerjet`, `infojobs`).

---

## 2. ACTIVE vs NEEDS_CREDENTIALS cross-check

Aligned with VALIDATION_REPORT + CREDENTIALED_CONNECTORS:

| Bucket | Keys |
|--------|------|
| ACTIVE (job connectors) | `remotive`, `arbeitnow`, `remoteok`, `working_nomads`, `weworkremotely`, `themuse`, `jobicy`, `himalayas`, `hn_whoishiring`, `devitjobs`, `nofluffjobs`, `getonbrd`, `mycareersfuture`, `jobup`, `nav_arbeidsplassen`, `landing_jobs`, `okemprego`, `jobbank_ca`, `devglobaljobs`, `viewjobs`, `kalibrr`, `dou_ua`, `authentic_jobs`, `wantedly`, `duunitori`, `jobindex`, `wanted`, `instahyre`, `hasjob`, `helloworld_rs`, `posao_hr`, `jobweb_kenya`, `tecnoempleo`, `le_forem`, `mpsv`, `findmethatdamjob`, `greenhouse`, `lever`, `ashby`, `smartrecruiters`, `arbetsformedlingen`, `reed` |
| NEEDS_CREDENTIALS (scaffolds in registry) | `adzuna`, `usajobs`, `france_travail`, `bundesagentur`, `jooble`, `findwork`, `careerjet`, `infojobs` |
| Catalog NEEDS_CREDENTIALS **without** registry connector | e.g. StepStone, XING, Indeed, LinkedIn, Malt, Upwork, … (documented; not inventable here) |

Keys alone never flip ACTIVE — need live insert + `promote_source_active.py` (CREDENTIALED_CONNECTORS).

---

## 3. Gap matrix by target region

“Have” = dedicated or strongly geo-tagged registry collector. “Bleed” = global remote / ATS / multi-EU that may include some roles but is not a national board.

| Region | Have (registry) | Status | Missing / thin |
|--------|-----------------|--------|----------------|
| **IT** | `infojobs` scaffold | NEEDS_CREDENTIALS | Dedicated IT board connector shipped; keys + partner ToS before ACTIVE. Ministero del Lavoro `UNDER_REVIEW`. Bleed: remote, `landing_jobs`, ATS, `careerjet`/`adzuna` when keyed. |
| **CH** | `jobup` | ACTIVE | Strong free Swiss search. Stats/procurement catalog rows (`SECO`, Salarium, SIMAP, SFSO) `UNDER_REVIEW` — not job ingest. No second CH board. |
| **LU** | `devglobaljobs` | ACTIVE | Free display API default includes `lu` (`DEVGLOBALJOBS_COUNTRIES`). Aggregator with attribution — not a national PES. Bleed: keyed `careerjet` `fr_LU`. |
| **DE** | `arbeitnow` ACTIVE; `bundesagentur` scaffold | ACTIVE + NEEDS_CREDENTIALS | Official PES blocked on keys + promote. Catalog StepStone/XING `NEEDS_CREDENTIALS` with **no** connector. |
| **FR** | `france_travail` only | NEEDS_CREDENTIALS | No free FR ACTIVE board. PES needs OAuth + Emploi Store / Offres v2; not ACTIVE until live ingest. |
| **ES** | `tecnoempleo` | ACTIVE | Spain IT RSS syndication. InfoJobs still `NEEDS_CREDENTIALS`. No Empléate Solr scrape (ADR-003). |
| **PT** | `okemprego` + `landing_jobs` | ACTIVE | Free okemprego API (`it-data`, default `pt`) + Landing.jobs EUR tech. IEFP remains scrape-only — skip (ADR-003). |
| **BE** | `le_forem` | ACTIVE | Wallonia ODWB open-data dump (Explore API). Partner HR-XML / VDAB out of scope. |
| **CZ** | `mpsv` | ACTIVE | Úřad práce volná místa open-data dump (JSON / JSON-LD stream). |
| **NL** | `findmethatdamjob` | ACTIVE | Documented public API (careers aggregator; not UWV PES). Bleed: `devitjobs` (`nl` host), keyed `adzuna` `nl`. **Werk.nl listings blocked** (no official API — see [NL_JOBS_COVERAGE.md](NL_JOBS_COVERAGE.md)). |
| **Nordics** | `arbetsformedlingen` (SE), `nav_arbeidsplassen` (NO), `duunitori` (FI), `jobindex` (DK) | All ACTIVE | Best regional coverage. Residual: official FI/DK PES (vs commercial boards), other Nordic markets (IS, …). |
| **UK** | `reed` ACTIVE; `devitjobs` ACTIVE; `adzuna` scaffold | ACTIVE + NEEDS_CREDENTIALS | Solid free path. Adzuna still NEEDS_CREDENTIALS. Find a Job DWP `UNDER_REVIEW`. |
| **US** | `usajobs` + `findwork` scaffolds; remote + ATS + `themuse` bleed | NEEDS_CREDENTIALS + Partial | Federal PES and Findwork not ACTIVE until keyed live ingest. Private market via remote/ATS only. |
| **CA** | `jobbank_ca` | ACTIVE | ESDC monthly open-data CSV (OGL-Canada) via CKAN; IT filter NOC21 + keywords. Point-in-time snapshot (search deep-link URLs). Bleed: remote/ATS. |
| **AU** | `viewjobs` | ACTIVE | Free MCP search (`/api/mcp` search_jobs; no key). Regional + metro AU. Not Seek scrape. ABS/LMI stats rows remain `UNDER_REVIEW`. Bleed: keyed Adzuna `au`. |

### Shared “bleed” layer (all regions)

These are ACTIVE but **not** national coverage substitutes:

- Remote: `remotive`, `remoteok`, `working_nomads`, `weworkremotely`, `jobicy`, `himalayas`, `authentic_jobs`, `hn_whoishiring`
- Multi-EU / tech: `arbeitnow`, `devitjobs`, `landing_jobs`
- ATS: `greenhouse`, `lever`, `ashby`, `smartrecruiters` (tenant allowlist)
- Multi-geo keyed: `jooble` (location env) — still NEEDS_CREDENTIALS

---

## 4. Biggest gaps — IT / CH / LU / DE (summary)

| Region | Severity | Have today | Biggest gap |
|--------|----------|------------|-------------|
| **IT** | High (blocked) | `infojobs` scaffold | Keys + partner path before ACTIVE; ministry catalog still not wired |
| **LU** | Medium | `devglobaljobs` ACTIVE | Aggregator coverage; no official LU PES API yet |
| **DE** | High (blocked) | `arbeitnow` ACTIVE | National PES (`bundesagentur`) + StepStone/XING stuck on credentials; scaffold exists only for BA |
| **CH** | Low–medium | `jobup` ACTIVE | Single-source dependency; no official PES job API path beyond JobUp |

**Operator unlock:** NL free path is `findmethatdamjob` (no key) + optional `adzuna` `nl` when keyed. AU free path is `viewjobs` (MCP). PT free path is `okemprego` + `landing_jobs`. Other scaffolds: `bundesagentur` (DE), `infojobs` (IT), `careerjet` (IT/DE/CH/LU), `jooble` / `adzuna` multi-geo; FR unlock is `france_travail`.

---

## 5. Related docs

- [VALIDATION_REPORT.md](VALIDATION_REPORT.md) — ACTIVE evidence
- [CREDENTIALED_CONNECTORS.md](CREDENTIALED_CONNECTORS.md) — env + promote gate
- [COVERAGE_GAPS.md](COVERAGE_GAPS.md) — role / source-type gaps
- `backend/app/collectors/registry.py` — `COLLECTORS`, `COLLECTOR_GEO`, `CREDENTIALED_SCAFFOLDS`
