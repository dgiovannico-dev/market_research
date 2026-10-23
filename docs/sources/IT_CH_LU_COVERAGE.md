# Coverage gap: Italy · Switzerland · Luxembourg

**Date:** 2026-10-22  
**Research agents:** IT / CH / LU deep web passes (same day)  
**Policy:** [ADR-003](../decisions/ADR-003-authorized-connectors-only.md) — public API / RSS / open data / written partner credentials only.  
**Related:** [GEO_PRIORITY_P0.md](GEO_PRIORITY_P0.md), [GEO_RESEARCH_IT_CH_LU_DE.md](GEO_RESEARCH_IT_CH_LU_DE.md), [plan](../superpowers/plans/2026-10-22-it-ch-lu-sources.md), **[IT_CH_INCREMENT_FEASIBILITY.md](IT_CH_INCREMENT_FEASIBILITY.md)** (2026-10-22 live corpus + increment scenarios)

## Bottom line

| Country | Live job ads (legal path today) | Demand / stats | Blocked / wrong in repo |
|---------|----------------------------------|----------------|-------------------------|
| **IT** | **ATS tenant allowlists** (Ashby/Greenhouse/Lever/Personio/…). Remote boards = eligibility, not employer demand. | Excelsior CC BY 4.0, Eurostat `isoc_sk_oja*`, Indeed Hiring Lab IT CSV, ISTAT SDMX | **InfoJobs.it closed** (API = Spain). EURES/Cliclavoro partner-only. No national PES vacancy API. |
| **CH** | **JobCloud affiliate** (ask contract); **Adzuna `ch`** + **Careerjet** with licence/publisher clarity; **ATS** (e.g. Swisscom Workday). | BFS vacancies, SECO open data, Swiss Job Tracker indices | **JobUp public `/api/`** conflicts with JobCloud ToS + `robots Disallow: /api/`. Job-Room `_search` needs SECO written consent. EURES partner-only. SwissDevJobs ToS bans reuse. |
| **LU** | **ATS tenants** (`country=lu`); thin **devglobaljobs**; LexGO (legal only). | **ADEM CC0** skills/vacancy open data on data.public.lu | EURES until ADEM NCO partnership. jobs.lu SOAP needs partner key. Moovijob/Monster: no path / shutdown. Adzuna has **no LU**. |

---

## Current repo inventory

| Geo | Collectors / catalog | Issue |
|-----|----------------------|-------|
| IT | `infojobs` → `COLLECTOR_GEO={"IT"}`, NEEDS_CREDENTIALS; `careerjet` locales include `it_IT`; Adzuna supports `it` but geo map often GB-only | InfoJobs geo **wrong** (ES API; IT site closed Dec 2025). No ACTIVE Italy-native board. |
| CH | `jobup` **ACTIVE** public search; Careerjet CH locales scaffolded | JobUp legal risk under ADR-003 — review / affiliate. |
| LU | `devglobaljobs` (defaults include LU); Careerjet `fr_LU` scaffold | ~14 LU rows on DevGlobalJobs probe — thin. ADEM open data documented but not wired as job connector. |

---

## Italy — prioritized findings

### P0 (build / seed now)

1. **Italian tech ATS allowlist** — expand `ats_boards` / Workday / Personio / SmartRecruiters tenants (verified: Satispay Ashby ~75, Scalapay Greenhouse ~10). Highest legal vacancy-level path.
2. **Excelsior Unioncamere–MLPS** — CC BY 4.0 commercial OK with attribution; file ingest of ICT professions + collaborator/non-employee shares (freelance proxy). Not live ads.
3. **Eurostat `isoc_sk_oja` / `oja2`** — official ICT mix in online ads (IT 2026-Q2 shares verified live).
4. **Indeed Hiring Lab IT aggregate CSV** — CC BY 4.0 trend index (no sector split).

### P1 (keys / written terms)

5. **Adzuna `it`** — expand `COLLECTOR_GEO`; **written commercial licence** before product aggregates.
6. **Careerjet `it_IT`** — activate scaffold after publisher retention terms in writing.

### Reject / reclassify

- InfoJobs.it closed → remap collector geo to **ES** (or disable for IT focus).
- EURES IT, SIISL/Cliclavoro, Indeed scrape, LinkedIn, Subito, Jooble bulk (500 lifetime), WTTJ without partnership.

---

## Switzerland — prioritized findings

### P0 (legal routes)

1. **JobCloud affiliate programme** — email `affiliates@jobcloud.ch`; XML/JSON feed under contract (jobs.ch + jobup + JobScout24). Replace unauthorized public API reliance.
2. **Adzuna `ch`** — API exists; commercial aggregation needs licence (same as IT).
3. **Careerjet `de_CH` / `fr_CH`** — publisher key; confirm storage rights (`it_CH` unverified).
4. **Employer ATS** — Swisscom Workday tenant + Personio CH allowlist.
5. **Stats context** — BFS quarterly vacancies; SECO registered-vacancies open data; Swiss Job Tracker (index, not ads).

### P1 (consent first)

6. **Job-Room** `POST …/jobadservice/api/jobAdvertisements/_search` — works as SPA backend; arbeit.swiss requires **written consent** to reproduce ads → ask `jobroom-api@seco.admin.ch` before ACTIVE.
7. **x28 AG** — commercial corpus behind Swiss Job Tracker (quote).

### Flag / avoid

- Keep JobUp ACTIVE only after legal review; do **not** add parallel `jobs.ch` public search (same inventory + same ToS).
- SwissDevJobs `jobsLight` JSON exists but ToS forbids reuse.
- EURES CH = partner via SECO NCO only (do not ship unofficial `jv-search` as production).

---

## Luxembourg — prioritized findings

### P0

1. **ADEM open data (CC0)** — skills-in-vacancies + chiffres-clés on data.public.lu; demand intelligence pipeline (not live job list). See [ADEM_LU_SKILLS_OPENDATA.md](ADEM_LU_SKILLS_OPENDATA.md).
2. **LU ATS tenants** — SmartRecruiters/Lever/etc. with `country=lu` (e.g. Talan probe OK).

### P1

3. Keep **devglobaljobs** (attribution; ~14 LU).
4. **Careerjet `fr_LU`** with publisher key.
5. Optional **LexGO** `https://www.lexgo.lu/api/v1/jobs` (legal sector; explicit machine terms).

### Partner track (no code until approved)

6. jobs.lu JobWS key + commercial reuse.
7. EURES via ADEM National Coordination Office.
8. Moovijob feed agreement.

---

## Live probes (2026-10-22, single requests)

| Probe | Result |
|-------|--------|
| EURES `locationCodes:["lu"]` + keyword software | HTTP 200, ~230 records (technically open; **partner ToS** → not production without NCO) |
| EURES `it` / `ch` software | ~315 / ~1586 records (same legal caveat) |
| JobUp public search software | HTTP 200, ~1242 hits (**ToS/robots conflict**) |
| SwissDevJobs `/api/jobsLight` | HTTP 200, 233 jobs (**ToS bans reuse**) |
| Job-Room `_search` without sort | HTTP 200 empty list; with `sort=datePublished,desc` → 400 (sort enum); agent verified `sort=date_desc` + body keywords |

---

## Acceptance (program)

- [x] IT: InfoJobs geo corrected to ES; ATS defaults include Satispay/Docebo/TheFork/TrueLayer/Moneyfarm/… (re-probe before expand); Eurostat OJA allowlisted (`isoc_sk_oja*`).
- [ ] IT: live crawl inserts tagged `IT` from new ATS tenants (ops: restart seed + run sources).
- [ ] CH: JobCloud affiliate **or** licensed Adzuna/Careerjet producing CH rows; JobUp legal decision recorded; no new scrape of JobCloud public API.
- [x] CH: Workday `juliusbaer:wd3:External` + Swisscom in defaults (Zurich/LU offices).
- [x] LU: ADEM skills-summary API (`GET /stats/adem/skills-summary` + CLI); ATS `Talan`/`Devoteam` SR; Careerjet when keyed.
- [ ] Catalog + GEO_PRIORITY_P0 updated; ADR-003 regressions avoided.
