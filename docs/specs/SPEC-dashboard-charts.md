# Spec: complete chart dashboard (Demand Compass cockpit)

**Status:** Accepted (2026-10-22) — implementation in progress  
**Extends:** [SPEC-dashboard.md](SPEC-dashboard.md), [SPEC-analytics.md](SPEC-analytics.md)  
**Policy:** [ADR-001](../decisions/ADR-001-evidence-first-kpis.md) (observed ≠ market size), [ADR-004](../decisions/ADR-004-dashboard-modes.md)

## Intent (shared understanding)

Build a **complete chart + table cockpit** so freelancers can read observed demand at a glance: volume trends, geo (including world map), skills/tech, rates, contract/remote/seniority mixes, **human language requirements in ads**, source/quality coverage, and focus-vs-market compare — without inventing market size.

**Assumptions (correct if wrong):**
1. “Lingua ricercata” = **human languages required by the employer** (IT/EN/DE/FR/…), stored as `Job.language_requirements` — **not** programming languages (those stay under Skills/Tech).
2. Prefer **one Executive cockpit** with scroll sections + deeper pages (Trends/Skills/Rates/Countries/Languages/Quality), not a separate product.
3. World map = **choropleth of observed job counts by ISO country** (ECharts map), not GIS heat of cities in v1.
4. Every chart keeps period, `n=`, thin-sample empty state, and **View as table**.

## Objective

Ship a chart-complete Demand Compass where:

1. Every product KPI in the catalog below has a **metric definition**, an **API field**, and a **primary visualization** (chart and/or sortable table).
2. Language requirements are first-class (extract → aggregate → chart/table).
3. Geography includes strip **and** world map.
4. Guided vs trends_only still apply (methodology walls only in guided).

## Out of scope

- Forecasting / saturation / “total Italian market size”.
- Causal claims from co-occurrence.
- Mixing Eurostat/ADEM/Excelsior **into** job KPIs (keep as optional **reference** panels, labeled `evidence_kind=official_statistics_reference`).
- 3D/WebGL vanity maps.
- Machine-translating job posting text.

---

## KPI catalog (complete)

Each KPI: `metric_key`, unit, definition, primary viz, API (existing or **new**), phase.

### A — Volume & momentum

| metric_key | Unit | Definition | Viz | API | Phase |
|------------|------|------------|-----|-----|-------|
| `unique_jobs_observed` | count | Deduped jobs with `published_at` in period | KPI tile | `summary` | Done |
| `jobs_per_day` | series | Daily observed unique jobs | Sparkline / area | `summary.jobs_per_day` | Done |
| `observed_demand_growth_pct` | % | vs previous equal window; or `insufficient_data` | KPI + badge | `summary` | Done |
| `new_jobs_first_seen` | count | First ingested in period (if `first_seen_at` usable) | KPI / spark overlay | **new** optional | P2 |
| `jobs_open_vs_closed` | share | Status mix in window | Stacked bar | **new** facets | P1 |

### B — Geography

| metric_key | Unit | Definition | Viz | API | Phase |
|------------|------|------------|-----|-----|-------|
| `jobs_by_country` | count | By `country_code` (unknown bucket) | GeoStrip + **world map** + table | `summary.top_countries` / `countries` | Map **P0** |
| `remote_share_by_country` | share | Remote among country slice | Grouped bar / table | `countries` | Done table → chart P1 |
| `freelance_share_by_country` | share | Freelance/B2B among country | Table → bars | `countries` | P1 |
| `jobs_unknown_country_pct` | share | Missing ISO | Quality callout | quality / summary | P0 |

### C — Work arrangement

| metric_key | Unit | Definition | Viz | API | Phase |
|------------|------|------------|-----|-----|-------|
| `remote_mix` | share | remote / hybrid / onsite / unknown | **Donut** | **new** `facets` or summary | P0 |
| `contract_mix` | share | freelance / b2b / contractor / employee / unknown | Donut / stacked | **new** facets | P0 |
| `seniority_mix` | share | When extracted | Horizontal bars | **new** facets | P1 |
| `freelance_b2b_verified` | count | Contract types with conf ≥ 0.7 | KPI tile | `summary` | Done |

### D — Skills & technology

| metric_key | Unit | Definition | Viz | API | Phase |
|------------|------|------------|-----|-----|-------|
| `top_technologies` | count | Observed skill tags | Ranked bars | trends / summary | Done list → chart P0 |
| `technology_rise_cool` | delta | Half-period compare | RiseCool | trends | Done |
| `skill_cooccurrence` | support/lift/jaccard | Pair stats | Heat or top-pairs bars | cooccurrence | Table done → heat **P1** |
| `combo_filters` | count | e.g. Java+AI, Python+LLM | Filter chips + KPI | documented filters | P2 |

### E — Compensation

| metric_key | Unit | Definition | Viz | API | Phase |
|------------|------|------------|-----|-----|-------|
| `rate_percentiles` | money | p25/p50/p75; NULL excluded | **Box/violin-lite** | rates | Chart **P0** |
| `jobs_with_published_rate` | count/share | Declared pay coverage | KPI | summary | Done |
| `rate_by_country` / `by_remote` | money | Slice medians when n≥threshold | Grouped bars / table | rates | P1 |
| `pay_kind_mix` | share | hourly/daily/yearly if present | Donut | rates | P1 |

### F — Human languages (**new product surface**)

| metric_key | Unit | Definition | Viz | API | Phase |
|------------|------|------------|-----|-----|-------|
| `language_requirements_top` | count | Ads mentioning required human language(s) | Ranked bars + table | **`GET …/languages`** | **P0** |
| `language_cooccurrence` | pairs | e.g. EN+IT, EN+DE | Pair bars | same endpoint | P1 |
| `language_by_country` | matrix | Top langs × country | Heat / stacked | languages | P1 |
| `jobs_with_any_language_req_pct` | share | Coverage of extraction | Quality KPI | languages + quality | P0 |
| `language_vs_profile` | count | Jobs matching profile.languages | KPI on Profile/Executive | profile + match | P2 |

**Data path:** populate `Job.language_requirements` (ISO 639-1 list) via rules (keywords / EURES-style codes / regex) at classify/ingest; never invent when absent (`[]` + evidence_kind).

### G — Sources & quality

| metric_key | Unit | Definition | Viz | API | Phase |
|------------|------|------------|-----|-----|-------|
| `jobs_by_source` | count | Per connector | Bars + table | quality | Chart P0 |
| `pct_thin_evidence` | share | Thin tier share | Callout + bar | quality / coverage_notes | Done notes |
| `extraction_coverage` | shares | rates / skills / country / languages | Radar or multi-bar | quality | P1 |
| `enabled_sources` | count | Ops | KPI | ops/summary | Done |

### H — Lenses (Demand Compass)

| metric_key | Unit | Definition | Viz | API | Phase |
|------------|------|------------|-----|-----|-------|
| `market_vs_focus_counts` | count | Parallel volume | CompareDual | lenses | Done |
| `focus_skill_overlap` | share | Focus skills in market | Dual bars | **extend** | P1 |
| `lens_sample_size` | count | Effective n under lens | Status line | all | Done |

### I — Reference only (separate panel, not job KPIs)

| metric_key | Notes | Phase |
|------------|-------|-------|
| Eurostat `isoc_sk_oja*` | ICT mix in OJA — labeled reference | P2 |
| ADEM LU skills open data | Demand baseline LU | P2 |
| Excelsior IT | Planned hires ICT | P2 |

---

## Chart inventory (complete)

| ID | Type | Data | Placement | Phase |
|----|------|------|-----------|-------|
| `rise_cool` | Diverging bars | tech trends | Executive hero, Trends | Done |
| `jobs_spark` | Sparkline/area | jobs/day | Executive | Done |
| `geo_strip` | H-bar top-N | countries | Executive, Countries | Done |
| `geo_world` | **Choropleth map** | jobs by ISO2 | Countries page + Executive below fold | **P0** |
| `compare_dual` | Dual line | market/focus | Compare lens | Done |
| `remote_mix` | Donut | remote facets | Executive aside, Countries | **P0** |
| `contract_mix` | Donut | contract facets | Executive aside | **P0** |
| `tech_rank` | Ranked bars | top technologies | Executive, Skills | **P0** |
| `cooccur_heat` | Heat / pair bars | co-occurrence | Skills | P1 |
| `rates_box` | Box / p25-p50-p75 | rates | Rates | **P0** |
| `lang_rank` | Ranked bars | language requirements | **Languages** page + Executive | **P0** |
| `lang_country_heat` | Heat | lang × country | Languages | P1 |
| `source_mix` | Bars | by source | Quality | **P0** |
| `seniority_bars` | H-bar | seniority | Trends / Quality | P1 |
| `status_stack` | Stacked | open/closed | Quality | P1 |

**Shared chart chrome (all):** `ChartFrame` period · `n=` · top-N · View as table · empty/thin · i18n · reduced-motion · dynamic import.

---

## Information architecture

### Executive (cockpit — scroll)

1. **Above fold (unchanged spirit):** brand · lens · status · hero `rise_cool` · CTAs  
2. **Strip:** KPI tiles (volume, growth, freelance verified, rate coverage, language coverage)  
3. **Momentum:** `jobs_spark`  
4. **Geo:** `geo_strip` + link “Open map”  
5. **Mix:** `remote_mix` + `contract_mix`  
6. **Tech:** `tech_rank`  
7. **Languages:** `lang_rank` (top 8)  
8. **Compare** (lens): `compare_dual`  

### New page: `/languages`

- `lang_rank` + sortable table (language, jobs, share, `n`)  
- Optional `lang_country_heat`  
- Coverage: % jobs with ≥1 language requirement  
- Guided: definition + limits (extraction incomplete; missing ≠ “no language required”)

### Countries page

- Existing table + `geo_world` choropleth + `geo_strip`  
- Click country → prefs country filter / deep link Jobs

### Skills / Rates / Quality / Trends

- Promote residual charts (`cooccur_heat`, `rates_box`, `source_mix`) from tables to primary viz with table toggle.

---

## API additions

| Endpoint | Purpose |
|----------|---------|
| `GET /api/v1/market/facets` | Aggregates: remote, contract, seniority, status (period, lens, country, min_evidence) |
| `GET /api/v1/market/languages` | Top languages, shares, optional by_country, coverage pct |
| `GET /api/v1/market/countries` | Extend with full ISO series for map (not only top-N) when `format=map` or always include `items` uncapped soft-limit |

All responses: `sample_size`, `period_days`, `definition`, `limits`, `evidence_kind`, optional `coverage_notes`.

### Classification / ingest

- Rules module: extract human languages → `Job.language_requirements` (list of `en`,`it`,…).  
- Backfill script for existing jobs.  
- Tests: fixtures with EN+IT requirements; empty when none.

---

## Acceptance criteria

- [ ] KPI catalog above mapped in docs; each P0 viz ships with table toggle and `n=`.
- [ ] World map renders observed countries; unknown not painted as a fake country; empty/thin states localized.
- [ ] Languages page + Executive `lang_rank` from real aggregates; missing languages honest.
- [ ] Facets API powers remote/contract donuts (no client-side full scan).
- [ ] Guided shows definitions/limits; trends_only keeps charts + `n=` only.
- [ ] IT/EN message keys for new chrome; parity check.
- [ ] Unit + API smoke for facets/languages; Playwright or DevTools smoke for map + languages route.
- [ ] No ADR-001 regression (no invented market totals).

## Key paths

- `frontend/components/charts/` (+ `GeoWorldMap`, `DonutMix`, `RankBars`, `RatesBox`, `LangRank`)
- `frontend/app/[locale]/languages/`
- `frontend/components/dashboard/ExecutiveDashboard.tsx` (section composition)
- `backend/app/analytics/facets.py`, `languages.py`
- `backend/app/classification/` language rules
- `docs/specs/SPEC-analytics.md` (cross-link)

## Approval gate

Approve this SPEC before implementation plan execution. Plan file: [../superpowers/plans/2026-10-22-complete-chart-dashboard.md](../superpowers/plans/2026-10-22-complete-chart-dashboard.md).
