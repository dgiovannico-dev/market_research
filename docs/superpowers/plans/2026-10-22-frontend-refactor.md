# Frontend quality & structure — refactor plan (senior)

**Date:** 2026-10-22  
**Scope:** `frontend/` (~139 TS/TSX, ~15k LOC)  
**Policy:** file ≤500 lines; SOLID/SRP; composition over boolean props  
**FSD layout:** execute via [2026-10-22-frontend-fsd-refactor.md](./2026-10-22-frontend-fsd-refactor.md) (Feature-Sliced Design waves)  

**Agents (all done):**
- [FE architecture](2ebdc847-e71b-41a0-aacf-f8b4c0be4bf6)
- [FE dashboards](1741bb33-33d6-4e87-9013-cdb8d359158b)
- [FE API client](f5dfdb6f-dde3-48cc-9d25-03904b849e96)
- [FE charts](197a6bce-ac9a-42cb-bb09-6b21b070a8b7)
- [FE research/ops](ecf6b807-6422-495e-a3df-9ce0aa874755)

---

## Overall verdict: **moderate refactor — necessary, not a rewrite**

Boundaries are mostly healthy (no circular deps; analytics pages thin; charts ≠ dashboard; research/explorer are the cohesion models). Debt clusters in:

1. Near-cap **`lib/api.ts` (492)** façade  
2. **Copy-paste dashboard** fetch/shell/table loop (Skills/Rates/Languages ~85% alike)  
3. **ChartFrame** god shell + full ECharts payload  
4. **Jobs / Catalog / credentials** fat client islands  

| Axis | Grade | Action |
|------|-------|--------|
| Architecture | Coherent feature layers; fat containers | Split Executive/Trends/Quality; sources folder |
| Dashboards | High duplication; sticky errors / stale data | Shared query hook + table shell (**P0 bugs first**) |
| API client | Partial split; untested contracts | Finish domain split; tests; fix `runSource` |
| Charts | Right grain; overloaded frame | `useChartTopN`; peel table; modular ECharts |
| Research / explorer | Healthy | Leave as reference |
| Jobs / ops | Client-heavy; raw ops fetch | Waves after dashboard extract |

**Do not rewrite.** Prefer vertical slices ≤1 day with behavior-preserving extractions + smoke.

---

## Priority backlog (execute in order)

### P0 — Correctness (before big extracts)
1. Sticky `error` never cleared on success (Skills/Rates/Languages/Trends/Countries) → clear on success / new request  
2. Languages + Trends: show loading when `!data && !error` (not premature empty)  
3. Soft-reset / `isStale` when lens|countries|period change (avoid wrong-lens UI)  
4. Optional: `AbortController` inside shared fetch hook  

### P1 — Highest leverage structure
5. Contract tests: `withLensQuery` + `apiHttp` / `ApiRequestError`  
6. Split `api.ts` → `apiMarket` / `apiAssistant` / `apiSources` + thin barrel  
7. Extract `useDashboardLensQuery` + `DashboardPageShell` + `DashboardLensHeader` + `CompareLensHints`  
8. Extract `SortableDataTable` (+ shared thead); migrate Skills → Rates → Languages → Countries → Trends  
9. `useChartTopN`; GeoStrip → RankBars; peel `ChartDataTable` from ChartFrame  
10. Fix `runSource` (+ ops UIs) to shared client / `ApiRequestError`  

### P2 — Size / feature folders / bundle
11. Split ExecutiveDashboard (hooks + header + methodology + top lists)  
12. Quality: shared `qualityTone` + thinner tables  
13. `components/sources/` for Catalog/credentials/runnable; typed catalog DTO  
14. Jobs toward explorer RSC shape (first page server; client load-more)  
15. ECharts modular `echarts/core` + self-host GeoJSON  
16. Unify period clamps (`useDashboardPeriodDays`)  
17. Cache `MarketCoverageBanner` discovery fetch  

### Explicit non-goals
- Full rewrite / new global state library without evidence  
- Breaking `@/lib/api` imports (keep barrel)  
- Touching research/* (reference module)  
- Mixing with IT/CH credential source work  

---

## Wave detail

### Wave A — API client ([FE API client](f5dfdb6f-dde3-48cc-9d25-03904b849e96))

| Task | Done when |
|------|-----------|
| A1 Tests `withLensQuery` + `apiHttp` | Green unit tests |
| A2 Split by domain; thin `api.ts` barrel | No impl file >~250; imports stable |
| A3 `runSource` → `requestJSON`; drop unused number overloads; `LensMeta`; doc days vs period_days | Typed errors; opts-only |
| A4 Unify ResearchJobs params; type sources enough for Sources page | Less `Record<string, unknown>` |

**Effort:** 1–2d. **Risk:** low.

### Wave B — Dashboards ([FE dashboards](1741bb33-33d6-4e87-9013-cdb8d359158b))

**Cluster A (~85%):** Skills ≈ Rates ≈ Languages — extract first.  
Trends ~72% (dual mode). Countries ~70% on table half. Quality/Exec/Relations: shell only.

| Task | Done when |
|------|-----------|
| B0 P0 bugfixes (error/stale/empty) | No sticky banner; no empty flash; stale opacity or clear |
| B1 `useDashboardLensQuery<T>` | 6+ dashboards use it |
| B2 `DashboardPageShell` + header + compare hints | Delete 8× Suspense wrappers duplication |
| B3 `SortableDataTable` | Skills/Rates/Languages migrated |
| B4 Period clamp helper; discovery banner cache | Consistent windows; ≤1 discovery fetch/session |

**Effort:** 2–3d. **Risk:** medium (fetch UX) — ship B0 first.

### Wave C — Architecture / god files ([FE architecture](2ebdc847-e71b-41a0-aacf-f8b4c0be4bf6))

| Task | Done when |
|------|-----------|
| C1 Shared lens payload helpers (nestPeriod / lensItems) | Executive ≡ Trends rules |
| C2 ExecutiveDashboard ≤250 orchestrator | Sections extracted |
| C3 TrendsTable extract | Dashboard thin |
| C4 Quality tone/types unified | Both files &lt;~280 |
| C5 CountryFilter split (url + control + provider) | Optional tidy |

**Effort:** 2–3d after Wave B shell exists.

### Wave D — Charts ([FE charts](197a6bce-ac9a-42cb-bb09-6b21b070a8b7))

| Task | Done when |
|------|-----------|
| D1 `useChartTopN`; GeoStrip→RankBars; drop HeatMatrix.showTopN | Less dup; no boolean mode |
| D2 ChartFrame → chrome only; `ChartDataTable` | Frame ~150; table hooks not always on |
| D3 Modular ECharts + GeoJSON vendor | Measurable chunk drop; map smoke OK |

**Effort:** D1 0.5d, D2 1d, D3 1–2d.

### Wave E — Research / jobs / ops ([FE research/ops](ecf6b807-6422-495e-a3df-9ce0aa874755))

**Leave alone:** `components/research/*`, `ApplicationsTable` + RSC applications page.

| Task | Done when |
|------|-----------|
| E1 Dead `JobsPagination`; `asJobRow`→lib; share URL parsers with explorer | Less dup |
| E2 Ops client + token hook; split CatalogBrowser; `components/sources/` | Typed; no raw ops fetch sprawl |
| E3 Jobs first-page RSC (optional) | Closer to explorer |
| E4 Assistant page → RSC shell + client islands | Thin page |

**Effort:** E1–E2 1–2d; E3–E4 optional later.

---

## Suggested calendar (2 weeks)

| Days | Focus |
|------|--------|
| 1 | **B0** dashboard bugfixes + **A1** API tests |
| 2–3 | **A2–A3** api split + runSource |
| 4–6 | **B1–B3** query hook + shell + SortableDataTable (Skills→Rates→Languages) |
| 7 | **D1–D2** chart quick wins + ChartFrame peel |
| 8–9 | **C1–C3** Executive/Trends/lens helpers |
| 10 | **E1–E2** sources/ops hygiene |
| Flex | D3 ECharts modular; E3 jobs RSC; C4–C5 |

---

## Acceptance (program)

- [ ] No `frontend` source file ≥500 lines; dashboards with logic ideally ≤300  
- [ ] Skills/Rates/Languages share one query + table shell (no sticky error / empty flash)  
- [ ] `api.ts` is barrel-only (&lt;80 lines) or clearly documented façade &lt;200  
- [ ] ChartFrame does not own table pagination machinery  
- [ ] Ops credentials use shared client; Catalog not a 300-line god  
- [ ] Smoke: `/`, `/trends`, `/skills`, `/rates`, `/quality`, `/jobs`, `/sources`, `/explorer` 200 + lens/country toggle OK  

---

## Bottom line

Refactor **yes, moderate**. Start with **P0 dashboard fetch bugs** and **API split/tests** — they unlock safer extracts. Research/explorer already show the target shape; Jobs/Catalog should converge toward that after the dashboard extract, not before.
