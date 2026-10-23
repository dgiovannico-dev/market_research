# IT / CH coverage — deep feasibility (can we increase?)

**Date:** 2026-10-22  
**Corpus:** local Compose DB (`jobs.is_canonical`), ~16.8k canonical rows  
**Policy:** [ADR-003](../decisions/ADR-003-authorized-connectors-only.md)  
**Prior research:** [IT_CH_LU_COVERAGE.md](IT_CH_LU_COVERAGE.md), [GEO_RESEARCH_IT_CH_LU_DE.md](GEO_RESEARCH_IT_CH_LU_DE.md), [plan](../superpowers/plans/2026-10-22-it-ch-lu-sources.md)

## Verdict

**Yes, it is possible to increase — but not by “adding random Italian boards.”**  
Italy has **no legal national vacancy API** left after InfoJobs.it closed. Switzerland already has JobUp volume, but the next step is **licence/partner**, not more public scrapers.

| Goal | Possible? | Main lever | Expected lift (order of magnitude) |
|------|-----------|------------|-------------------------------------|
| More **live job ads** tagged `IT` | Yes, gated | Adzuna `it` + Careerjet `it_IT` + ATS tenants | **×3–×20** if keys+licence; ATS alone **×1.5–×3** |
| More **live job ads** tagged `CH` | Yes, gated | Adzuna `ch` + Careerjet + JobCloud affiliate | **×2–×10**; JobCloud = market-scale |
| Fix “too low” via **geo backfill only** | Marginal | `country_backfill` on `unknown` | **~+20 rows** with clear city strings (not material) |
| Richer **demand intel** without ads | Yes, free | Excelsior / Eurostat OJA / BFS-SECO | Improves context panels, **not** Countries KPI counts |

---

## 1. Live baseline (evidence)

| Slice | Canonical jobs |
|-------|----------------|
| Total | ~16 809 |
| `unknown` | ~3 016 (~18%) |
| US / GB | ~2 373 / ~1 623 |
| CH | **~677** |
| IT | **~169** |
| SE (Arbetsförmedlingen) | ~964 — shows what a national ACTIVE board does |

### IT by source today

Almost entirely ATS / remote spillover — **no Italy-native ACTIVE board**:

| Source | IT n (approx) | Notes |
|--------|---------------|-------|
| Ashby | ~69 | ElevenLabs ~39, Satispay ~29 |
| Greenhouse / Workable / Arbeitnow | ~20 each | Moneyfarm (Workable) works; Deliveroo GH |
| SmartRecruiters / Workday | ~12–17 | |
| Others | &lt;10 | |
| Lever `musixmatch` / Pinpoint `bendingspoons` | **0 IT** | Seeded as IT focus but jobs tagged US/GB/JP/unknown — geo tagging bottleneck |

**Eurostat OJA:** module allowlists `isoc_sk_oja*`; FastAPI query `Literal` historically omitted them (422). Fixed to match `ALLOWED_DATASETS`. Still **reference** stats, not Countries KPI rows. Excelsior / Indeed Hiring Lab / Ministero SPARQL: docs only, no job ingest.

### CH by source today

| Source | CH n (approx) | Notes |
|--------|---------------|-------|
| **JobUp** | ~423 (62%) | Cap `MAX_RECORDS=150` / `MAX_PAGES=3` per collect — DB total is multi-query accumulation |
| Arbeitnow | ~198 (29%) | |
| Workday | ~14 | Swisscom ~7; other tenants trickle |
| SmartRecruiters / Robert Half / Greenhouse | ~8–10 each | |
| Personio | **0** | DACH allowlist present; no CH rows yet |

CH evidence mix ≈ 646 `standard` / 31 `thin`. ~668 of 677 fall in the 90-day countries KPI window.

**ADR-003 tension:** JobUp public `/api/` is the main CH board today, while docs flag JobCloud ToS + `robots Disallow: /api/` — scale only after legal review or **affiliate** replacement (not a parallel jobs.ch public scrape).

Dashboard `GET /market/countries` shows a **focus list** (`FOCUS_COUNTRIES` in `backend/app/analytics/countries.py`) — IT/CH are in scope; low counts are real corpus gaps, not UI filtering.

---

## 2. Why Italy is structurally thin

1. **InfoJobs.it closed** (2025-12-31). Repo `infojobs` collector talks to **Spain** `api.infojobs.net` — cannot refill Italy.
2. **No Italian PES public vacancy API** (Cliclavoro/SIISL/EURES = partner-only; Ministero SPARQL = fragile, deferred).
3. **Credentialed aggregators exist in code but are off:**
   - `adzuna` — `ADZUNA_APP_ID/KEY` **empty**; multi-country (`it`,`ch`,…) already in collector + `COLLECTOR_GEO`
   - `careerjet` — key empty; locales include `it_IT`
   - `jooble` — free tier **500 lifetime requests** → probe only, not a production IT pipeline
4. **ATS discovery hit a wall:** slug probe of Reply/TeamSystem/Zucchetti/Aruba/… returned essentially **zero** IT boards; only SmartRecruiters `Alten` (FR-heavy).
5. **Geo backfill headroom is tiny:** dry-run of `backfill_country_codes` updated **0/3016** unknowns when city hints were missing (IT = `italy`/`italia` only; CH = country words + Zurich). With expanded city hints (Milan/Basel/Bern/Geneva/…), recoverable text ≈ **+5 IT / +19 CH (~3% each)** — Workday/Greenhouse unknowns are mostly “N Locations” / US / remote, not IT/CH cities.

---

## 3. Why Switzerland looks better but still “low”

- JobUp already supplies the majority of CH rows (ACTIVE public search).
- Docs flag **JobCloud ToS / robots Disallow:/api/** conflict — keep ACTIVE only with legal eyes; prefer **affiliate contract** for jobs.ch + jobup + JobScout24.
- Blocked without consent: Job-Room `_search`, SwissDevJobs (ToS bans reuse), unofficial EURES.
- Same credential gate as IT for Adzuna `ch` / Careerjet `de_CH`/`fr_CH`.

---

## 4. Increment scenarios (decision matrix)

### A — Code-only, no keys (this week)

| Action | Impact | Risk |
|--------|--------|------|
| Expand IT/CH city hints + run `backfill_country_codes` | **Done 2026-10-22:** +4 IT / +20 CH (IT 169→173, CH 677→697); ~2992 unknown remain | Low |
| Expand ATS allowlist (manual careers → Greenhouse/Ashby slug) | +tens to low hundreds IT if 10–30 real tenants found | Medium effort; probe-first |
| Wire Excelsior / Eurostat OJA as **reference** panels | Demand story ↑; Countries KPI unchanged | Low (Eurostat client already allowlists `isoc_sk_oja*`) |

**Net:** measurable but **cannot** make IT look like SE/CZ.

### B — Self-serve keys + written licence (highest ROI)

| Action | Feasibility | Volume estimate* |
|--------|-------------|------------------|
| Enable **Adzuna** with `ADZUNA_COUNTRIES=it,ch,...` | Code ready (`adzuna.py`: 50×2 pages / country / query) | Per crawl query: up to ~100 ads/`it` + ~100/`ch`; across query fan-out + scheduler → **hundreds–low thousands** IT/CH over days |
| Enable **Careerjet** `it_IT`,`de_CH`,`fr_CH` | Scaffold ready | Overlap with Adzuna; useful fill; confirm **storage/analytics** ToS |
| Skip Jooble as primary | Quota fatal | Probe only |

\*Not a census: Adzuna returns snippets; commercial aggregation needs **written licence** after trial ([GEO_PRIORITY_P0](GEO_PRIORITY_P0.md), [CREDENTIALED_CONNECTORS](CREDENTIALED_CONNECTORS.md)).

### C — Partner tracks (market-scale CH / honest IT)

| Partner | Ask | If granted |
|---------|-----|------------|
| JobCloud `affiliates@jobcloud.ch` | XML/JSON feed + analytics rights | CH can approach national commercial board scale |
| SECO `jobroom-api@seco.admin.ch` | Read/search for analytics | Official CH PES ads |
| Adzuna / Careerjet sales | Commercial retention | Clears product use of B |
| Italian NCO / EURES | Partner API | Only path to “PES Italy” volume |

**Do not ship:** LinkedIn, Indeed HTML, Subito, EURES SPA, SwissDevJobs reuse, Job-Room scrape without consent.

### D — Wrong expectation to kill

Treating Countries KPI as a **full labour-market census**. Disclaimer already says observed DB rows. Even with Adzuna+JobCloud, Compass remains a **sampled tech/ATS/aggregator** lens unless PES partners land.

---

## 5. Recommended sequence

```
1. Ops: set Adzuna (+ Careerjet) keys via Fonti / env; ADZUNA_COUNTRIES includes it,ch
2. Live run → promote_source_active when inserts > 0
3. Parallel: ATS IT discovery from careers pages (not blind slug guessing)
4. Emails: JobCloud affiliate; SECO Job-Room read; Adzuna commercial
5. Stats path: Excelsior + Eurostat OJA panels (evidence_tier = official_statistics_reference)
6. Legal decision on JobUp public API vs affiliate-only
```

**Acceptance for “IT/CH no longer embarrassingly thin”:**

- IT canonical ≥ **1 000** from authorized paths, or explicit coverage note “ATS+aggregator sample”
- CH canonical ≥ **2 000** **or** JobCloud/Adzuna CH ACTIVE with licence checklist
- InfoJobs geo documented as ES-only in catalog/UI

---

## 6. Bottom line for product

| Question | Answer |
|----------|--------|
| È un bug? | No — mix di fonti ACTIVE sbilanciato (ATS US/GB + PES nordici) |
| Si può incrementare? | **Sì**, soprattutto con **Adzuna/Careerjet** e partner CH |
| Basta più codice senza chiavi? | **No** per un salto di ordine di grandezza su IT |
| InfoJobs salva l’Italia? | **No** — sito IT chiuso; API = Spagna |
| Backfill `unknown`? | Recupero **irrilevante** (~20) |
| Open data Excelsior/Eurostat? | Utile per **domanda**, non per conteggio annunci live |

---

## Sources (this pass)

- Live SQL on Compose `jobs` / `sources` (2026-10-22)
- `backend/app/collectors/{adzuna,registry}.py`, `ingestion/country_backfill.py`, `analytics/countries.py`
- `docs/sources/IT_CH_LU_COVERAGE.md`, `GEO_PRIORITY_P0.md`, `CREDENTIALED_CONNECTORS.md`, ADR-003
- Adzuna search docs: https://developer.adzuna.com/docs/search
- Failed IT ATS slug probe (Reply/TeamSystem/…): only Alten SR (non-IT geo mix)
