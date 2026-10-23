# Complete chart dashboard — Implementation Plan

> **For agentic workers:** Implement task-by-task after SPEC approval. Steps use checkbox syntax.

**Goal:** Deliver a chart-complete Demand Compass cockpit (counts, mixes, rates, geo map, human languages) wired to evidence-first analytics.

**Architecture:** New analytics modules (`facets`, `languages`) + language extraction rules; ECharts lazy wrappers; Executive sections below the hero; new `/languages` route; world choropleth on Countries.

**Tech Stack:** FastAPI/SQLAlchemy analytics, Next.js App Router, ECharts (`echarts-for-react` + `echarts/map` world JSON), next-intl, existing `ChartFrame` / top-N patterns.

**Spec:** [SPEC-dashboard-charts.md](../../specs/SPEC-dashboard-charts.md)

## Global Constraints

- ADR-001: observed counts only; every metric carries definition / sample / limits.
- File size ≤500 lines; split chart wrappers and analytics modules.
- Dynamic-import heavy ECharts (especially world map).
- Table toggle on every new chart.
- IT/EN key parity for new copy.

## Review Focus

1. Map paints only ISO codes present in data (no fake “world total”).
2. Language extraction false positives (e.g. “Java” ≠ language).
3. Facets query performance on large `jobs` tables (indexes / evidence gate).
4. Bundle size of world map asset.
5. Guided vs trends_only still hides methodology walls correctly.

## File map

| Area | Files |
|------|--------|
| Analytics | `backend/app/analytics/facets.py`, `languages.py`; wire `market_extra.py` / router |
| Extract | `backend/app/classification/language_rules.py`; call from classify/ingest path |
| Backfill | `backend/scripts/backfill_language_requirements.py` |
| Charts | `frontend/components/charts/{DonutMix,RankBars,RatesBox,GeoWorldMap,LangRank}.tsx` + `lazy.tsx` |
| Pages | `app/[locale]/languages/page.tsx`; extend Countries + Executive + Rates + Quality + Skills |
| i18n | `messages/en.json`, `it.json` |
| Nav | `lib/navZones.ts` — Languages under Explore or Jobs zone |
| Tests | `test_facets.py`, `test_languages_analytics.py`, `test_language_rules.py`, API smoke |

---

## Task 1 — Facets API + remote/contract donuts (P0)

**Deliverable:** `GET /api/v1/market/facets` + Executive `remote_mix` / `contract_mix`.

- [x] Write failing tests for facet counts (remote/contract) with fixture jobs.
- [x] Implement `facets.py` using `base_job_query` + lens + country + `min_evidence`.
- [x] Expose route; document in OpenAPI/smoke.
- [x] Add `DonutMix` chart + lazy export; wire Executive below geo strip.
- [x] i18n keys; View as table.
- [x] Verify: smoke + Executive renders donuts with `n=`.

## Task 2 — Language rules + backfill (P0)

**Deliverable:** `Job.language_requirements` populated for new + backfilled jobs.

- [x] Failing tests: “English and Italian required” → `["en","it"]`; “Java developer” alone → `[]`.
- [x] Implement `language_rules.py` (keyword/ISO maps; exclude programming-language false friends).
- [x] Hook into classification/ingest upsert path.
- [x] Backfill script (batched); dry-run flag.
- [x] Verify: unit tests green; sample backfill on compose DB.

## Task 3 — Languages analytics + page (P0)

**Deliverable:** `GET /api/v1/market/languages` + `/languages` UI + Executive `lang_rank`.

- [x] Tests for top languages / coverage pct / empty.
- [x] Implement `languages.py` (unnest JSON array; group by code).
- [x] `LangRank` / reuse `RankBars`; Languages page with sortable table.
- [x] Nav zone entry; i18n.
- [x] Verify: API smoke + page load with real data or empty state.

## Task 4 — World map + full country series (P0)

**Deliverable:** `geo_world` on Countries (+ link from Executive).

- [x] Extend countries endpoint or add `?for_map=1` returning all ISO counts (cap e.g. 250).
- [x] `GeoWorldMap` with ECharts world geoJSON (pin version; license note in file header).
- [x] Click → set country filter / navigate Jobs `?country=` (Countries + filter chrome).
- [x] Unknown country excluded from map; shown in table footer.
- [x] Verify: Countries page map + table; reduced-motion OK.

## Task 5 — Rates box + tech rank + source mix (P0)

**Deliverable:** Promote residual SPEC-dashboard charts.

- [x] `RatesBox` from rates percentiles API on Rates page.
- [x] `RankBars` for top technologies on Executive/Skills/Languages.
- [x] `source_mix` bars on Quality from quality-by-source.
- [x] Verify: each has table toggle; thin-sample gate.

## Task 6 — Co-occurrence heat + seniority + lang×country (P1)

Shipped on **Relations** ([SPEC-correlative-relations.md](../../specs/SPEC-correlative-relations.md)); Skills keeps table co-occurrence.

- [x] `cooccur_heat` (Relations → Skills group).
- [x] seniority × tech heat (Relations); facets expose seniority.
- [x] `lang_country_heat` (Relations → Place group).
- [x] Verify: min_support / empty states; Skills/Place sub-tabs.

## Task 7 — Reference panels + polish (P2)

- [x] Optional Eurostat OJA / ADEM summary cards labeled reference-only.
- [ ] Combo filter chips (Java+AI etc.) if product prioritizes.
- [ ] Profile language match KPI.
- [x] Update ROADMAP (Relations + scheduler); chart plan checkboxes (2026-10-22).

## Dependency order

```
Task1 (facets/donuts) ──┐
Task2 (lang extract) ───┼──► Task3 (languages UI)
                        ├──► Task5 (rates/tech/source)  [parallel with 3]
Task4 (map) ────────────┘
Task3+4+5 ──► Task6 ──► Task7
```

## Test plan (program)

- [x] `pytest` facets, languages, language_rules (+ Relations matrix/series)
- [x] API smoke new routes
- [x] Manual: Executive; `/languages`; Countries map; Rates box; `/relations`
- [x] Message key parity en↔it (Relations keys added)
- [x] Bundle: map chunk lazy-only on Countries/Languages routes
