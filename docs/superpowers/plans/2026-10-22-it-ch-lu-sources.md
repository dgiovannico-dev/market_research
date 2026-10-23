# Plan: IT / CH / LU source inclusion

**Research:** [IT_CH_LU_COVERAGE.md](../../sources/IT_CH_LU_COVERAGE.md)  
**Policy:** ADR-003, ADR-005  
**Goal:** Close demand gaps for Italy, Switzerland, Luxembourg with **authorized** paths only.

## Architecture decisions (from research)

1. **Do not treat EURES `jv-search` as a free production connector** until NCO/partner admission (IT/CH/LU portal terms ban automated extraction for republication).
2. **InfoJobs collector is Spain**, not Italy — remap geo; IT site closed end-2025.
3. **JobUp public API** is ACTIVE but conflicts with JobCloud ToS/`robots` — prefer affiliate contract; pause expansion of JobCloud public endpoints.
4. **Vacancy-level coverage** for IT/LU (and CH backup) = **ATS tenant allowlists** + credentialed aggregators with written licences.
5. **Demand baselines** = open data (Excelsior, Eurostat OJA, ADEM CC0, BFS/SECO) in a **stats/evidence** path, not mixed as live job ads without clear evidence_tier.

## Dependency order

```
Legal / partner emails (JobCloud, SECO Job-Room, Adzuna, Careerjet, ADEM/EURES)
        │
        ├── Fix infojobs geo IT→ES + docs
        ├── ATS seeds: IT tech + LU employers + CH (Swisscom/Personio)
        ├── Open-data slices: ADEM LU, Excelsior IT, Eurostat OJA (optional ISTAT/BFS)
        ├── Activate Adzuna it/ch + Careerjet locales when keys + licence OK
        └── Later: JobCloud affiliate ingest; Job-Room if SECO consents; jobs.lu SOAP
```

## Tasks (vertical slices)

### T0 — Corrections & legal flags (do first)

- Remap `COLLECTOR_GEO["infojobs"]` from `IT` → `ES`; catalog notes: Spain API; IT closed.
- Document JobUp ToS/robots conflict in catalog + GEO_PRIORITY; decision: affiliate vs deprecate ACTIVE.
- Update [GEO_PRIORITY_P0.md](../../sources/GEO_PRIORITY_P0.md) Critical gaps table (InfoJobs IT claim obsolete).

**Done when:** registry + catalog + priority docs consistent; no claim that InfoJobs covers Italy.

### T1 — ATS allowlists (P0 live ads)

**IT:** seed ~50–100 tech employers (Satispay, Scalapay, …) across Ashby/Greenhouse/Lever/Personio/SmartRecruiters/Recruitee.  
**LU:** add SmartRecruiters/Lever/… tenants with `country=lu` filter.  
**CH:** add Swisscom Workday (`swisscom:wd103:SwisscomExternalCareers`) + Personio CH list.

**Files:** `docs/sources/ATS_TENANTS.md`, `ats_boards` / `workday` / `smartrecruiters` config, probes via `probe_ats_tenants.sh`, tests.

**Done when:** smoke shows inserts with `country_code` in `{IT,CH,LU}` from ATS sources.

### T2 — Open-data demand baselines (P0 context)

1. **ADEM LU** CC0 skills/chiffres-clés → stats ingest (extend [ADEM_LU_SKILLS_OPENDATA.md](../../sources/ADEM_LU_SKILLS_OPENDATA.md)).
2. **Excelsior IT** — downloadable bulletin/XLSX loader for ICT CP2011 codes + non-employee share.
3. **Eurostat** `isoc_sk_oja` / `oja2` for IT (reuse eurostat client patterns if present).
4. Optional: Indeed Hiring Lab IT CSV; ISTAT `534_1038`; BFS/SECO CH vacancy stats.

**Done when:** at least one LU + one IT open-data path produces stored evidence (tier = stats/open_data).

### T3 — Credentialed aggregators (P1, licence-gated)

1. Expand Adzuna `COLLECTOR_GEO` / `ADZUNA_COUNTRIES` to include **`it`**, **`ch`** (not LU — unsupported).
2. Activate Careerjet with locales `it_IT`, `de_CH`, `fr_CH`, `fr_LU` after written retention terms.
3. Promote catalog ACTIVE only after live inserts + licence checklist.

**Done when:** keyed smoke inserts for IT and CH from ≥1 of {adzuna, careerjet}.

### T4 — Partner tracks (no collector until approved)

| Partner | Ask for | Owner |
|---------|---------|-------|
| JobCloud | Affiliate/XML-JSON feed + analytics/storage rights | CH P0 legal |
| SECO Job-Room | Read/search licence for `_search` | CH P1 |
| ADEM / EURES NCO | Partner API for LU (and IT NCO for IT) | LU/IT P2 |
| jobs.lu | JobWS `SearchJobs` key + redistribution | LU P1 |
| Adzuna | Commercial aggregation licence | IT/CH |
| Careerjet | Explicit storage/analytics OK | IT/CH/LU |

### T5 — Focus / discovery (P1)

- Discovery probes + optional dashboard country defaults emphasizing IT, CH, LU.
- Coverage notes when sample thin for those countries.

### Explicit non-goals

- Shipping EURES `jv-search` as ACTIVE without NCO.
- New JobCloud public `/api/` collectors (`jobs_ch`).
- InfoJobs as Italy source; Indeed/LinkedIn/Subito/Moovijob scrape; SwissDevJobs; Jooble as primary (500 lifetime).

## Risks

| Risk | Mitigation |
|------|------------|
| ATS-only = incomplete market | Pair with Excelsior/Eurostat/ADEM stats; pursue Adzuna/JobCloud licences |
| JobUp already ACTIVE under ToS conflict | Legal decision ticket; throttle; pursue affiliate |
| Adzuna free key used for commercial KPIs | Gate aggregates behind licence flag |
| Partner emails stall | Ship ATS + open data first so product unblocks |

## Test plan

- [ ] Unit: infojobs geo ES; ATS tenant country filters
- [ ] Live/optional: ATS smoke IT/CH/LU; Adzuna/Careerjet when keys
- [ ] Open-data: ADEM/Excelsior/Eurostat parsers with fixtures
- [ ] Catalog seed + CREDENTIALED docs updated
- [ ] Manual: Jobs list filter country IT/CH/LU after runs
