# Frontend refactor — Feature-Sliced Design (FSD)

**Date:** 2026-10-22  
**Method:** [Feature-Sliced Design](https://feature-sliced.design/docs/get-started/overview) — incremental adoption  
**Companion:** quality findings in [2026-10-22-frontend-refactor.md](./2026-10-22-frontend-refactor.md)  
**Stack:** Next.js App Router + next-intl (locale already under `app/[locale]`)

---

## 1. Verdict

Adopt FSD **incrementally** — do not big-bang-move 139 files in one PR.

The current tree is already half-aligned (thin pages, feature folders for `research` / `explorer` / `jobs` / `assistant`). Gaps vs FSD:

| Gap | Today | FSD target |
|-----|--------|------------|
| No formal layers | flat `components/` + `lib/` + `hooks/` | `app` → `pages` → `widgets` → `features` → `entities` → `shared` |
| Import freedom | anything → `@/lib/api` | lower layers only; public API per slice (`index.ts`) |
| Fat “dashboard” hub | one folder owns all analytics | **widgets** per screen + **features** (lens, country, prefs) + **entities** (job, source, intent) |
| Shared leak | charts typed to API DTOs; root ops files | entities/api types; widgets compose |
| Next.js `app/` | route shells + layout | keep as FSD **App** layer (routing/providers only) |

**Refactor grade stays moderate:** same P0 bugs and extracts, reorganized as layer migration waves.

---

## 2. Layer map (project-specific)

```
┌─ app/          Next App Router, providers, global styles, middleware, i18n routing
├─ pages/        Route compositions (thin): home, trends, skills, sources, …
├─ widgets/      Full use-cases on a page: ExecutiveDashboard, SkillsPanel, CatalogBrowser, …
├─ features/     User actions / product capabilities: lens-toggle, country-filter, propose-brief, run-source, …
├─ entities/     Business nouns: job, source, research-intent, market-kpi, coverage-note, …
└─ shared/       UI kit, apiHttp, table hooks, formatters, config — no business meaning
```

**Import rule (hard):** a module may import only from **strictly lower** layers.  
Slices on the **same** layer must not import each other (cross via lower layer or lift to a shared feature).

```
app → pages → widgets → features → entities → shared
```

Deprecated FSD `processes/` — **do not use**.

---

## 3. Current → target mapping

### App layer (`frontend/app`, `middleware`, `i18n`, styles)

| Keep / move | Notes |
|-------------|--------|
| `app/[locale]/layout.tsx` | Providers only: prefs, country boundary, chrome |
| `app/[locale]/*/page.tsx` | Eventually re-export or compose `pages/*` widgets; short-term can stay as thin FSD “pages” in place |
| `middleware.ts`, `i18n/*`, `messages/*` | App/shared config |

Next.js forces routes under `app/`. Pragmatic FSD:

- **Phase 1–2:** treat `app/[locale]/x/page.tsx` as the **pages** slice entry (no second `pages/` tree yet).  
- **Phase 3 (optional):** introduce `src/pages/x` and import from `app/.../page.tsx` if you want textbook layout; not required for value.

### Pages (route entries — thin)

| Route | Composes widgets |
|-------|------------------|
| `/` | `widgets/executive-dashboard` |
| `/trends`, `/skills`, `/rates`, `/languages`, `/countries`, `/quality`, `/relations` | matching analytics widgets |
| `/jobs`, `/explorer` | `widgets/jobs-list`, `widgets/explorer` |
| `/focus`, `/market-scan` | `widgets/focus-panel`, `widgets/market-scan` |
| `/sources` | `widgets/sources-catalog` + `widgets/credentialed-connectors` |
| `/assistant` | `widgets/demand-compass` + `widgets/propose` |
| `/applications`, `/alerts`, `/profile` | corresponding widgets |

### Widgets (screen-sized)

| Slice | From today |
|-------|------------|
| `executive-dashboard` | `ExecutiveDashboard` (+ extracted sections) |
| `trends-dashboard`, `skills-dashboard`, `rates-dashboard`, `languages-dashboard`, `countries-dashboard`, `quality-dashboard`, `relations-dashboard` | matching `*Dashboard.tsx` |
| `jobs-list` | `JobsListDashboard` + filters/table |
| `explorer` | Explorer list + search form (form may be feature) |
| `sources-catalog` | `CatalogBrowser` |
| `credentialed-connectors` | `CredentialedConnectors` + editor shell |
| `focus-panel`, `market-scan` | research panels |
| `demand-compass`, `propose` | assistant sections |
| `app-chrome` | `AppChrome` + primary nav |

### Features (product actions)

| Slice | From today | Segments |
|-------|------------|----------|
| `lens-toggle` | `LensToggle` | `ui`, `model` (URL/prefs sync) |
| `country-filter` | `CountryFilter` + boundary | `ui`, `model` |
| `dashboard-prefs` | `DashboardPrefsProvider` + `PrefsPanel` | `ui`, `model`, `api` (persist) |
| `period-chip` | `PeriodChip` | `ui` |
| `run-source` / `run-free-sources` | `RunSourceButton`, … | `ui`, `api` |
| `ops-credentials` | `CredentialEditor` token+CRUD | `ui`, `api` |
| `propose-watch` | `ProposeSection` | `ui`, `api` |
| `create-focus-intent` | `CreateFocusForm` | `ui`, `api` |
| `table-guide` usage wrappers | optional — or stay shared/ui | — |

### Entities (nouns)

| Slice | Responsibility | Segments |
|-------|----------------|----------|
| `job` | `JobItem`, explorer/job mappers, `asJobRow`, list params | `model`, `api`, `lib` |
| `source` | catalog/source DTOs, status badges, evidence helpers | `model`, `api`, `ui` |
| `research-intent` | intents CRUD types + `researchApi` | `model`, `api` |
| `market` | KPIs, trends, countries, facets, languages, cooccurrence DTOs + GETs | `model`, `api` |
| `quality` / `rate` | quality & rates payloads | `model`, `api` |
| `relation` | matrices / series (`apiRelations`) | `model`, `api` |
| `coverage-note` | single `CoverageNote` type (kill dup) | `model`, `ui` |
| `assistant` | brief/propose types + client | `model`, `api` |

### Shared

| Segment | Contents |
|---------|----------|
| `shared/api` | `apiHttp`, `ApiRequestError`, `withLensQuery` (lens params are cross-cutting transport) |
| `shared/ui` | `SortableTh`, `TableGuide`, `TableSearch`, `MetricLegend`, `ScrollLoadFooter`, `MultiSelectFacet`, later `SortableDataTable`, `ChartFrame` chrome, RankBars/Donut (generic viz) |
| `shared/lib` | `tableFilter`, `tableSort`, `formatDateTime`, `formatPercent`, chart theme / topN |
| `shared/hooks` | `useClientTableSort/Filter/PageWindow`, `useInfiniteSentinel`, later `useChartTopN` |
| `shared/config` | `navZones`, env-facing constants |

**Charts policy:** generic ECharts primitives → `shared/ui` (or `shared/ui/charts`). Domain-specific option builders that need entity types → `entities/*/ui` or widget-local. Prefer not to create a parallel `charts` layer outside FSD.

---

## 4. Target tree (illustrative)

```
frontend/
  app/                          # App layer (Next)
    [locale]/layout.tsx
    [locale]/skills/page.tsx   # → widgets/skills-dashboard
    …
  src/                          # optional; or keep roots at frontend/
    widgets/
      skills-dashboard/
        ui/SkillsDashboard.tsx
        model/useSkillsData.ts  # or features via useDashboardLensQuery
        index.ts
      …
    features/
      lens-toggle/{ui,model,index.ts}
      country-filter/{…}
      dashboard-prefs/{…}
    entities/
      market/{api,model,index.ts}
      job/{api,model,lib,index.ts}
      source/{…}
    shared/
      api/{http.ts,query.ts}
      ui/{…}
      hooks/{…}
      lib/{…}
```

**Alias:** `@/` → `src/` (or keep `@/` = frontend root and use `@/widgets`, `@/features`, …). Prefer introducing `src/` only if you’re ready to move paths; otherwise place `widgets/`, `features/`, `entities/`, `shared/` next to `app/`.

**Recommended for this repo (minimal churn):**

```
frontend/
  app/
  widgets/
  features/
  entities/
  shared/
  # deprecate growing components/ and lib/ via moves
```

---

## 5. Public API rule (per slice)

Every slice exports only through `index.ts`:

```ts
// widgets/skills-dashboard/index.ts
export { SkillsDashboard } from "./ui/SkillsDashboard";
```

Pages/widgets import `@/widgets/skills-dashboard`, never deep paths into another slice’s internals.

Enforce later with [Steiger](https://github.com/feature-sliced/steiger) / ESLint boundaries (optional Wave F).

---

## 6. Migration waves (FSD + prior P0/P1)

Aligned with [incremental FSD adoption](https://feature-sliced.design/docs/get-started/overview#incremental-adoption): Shared/App foundation → Widgets/Pages → Features/Entities → fix import violations.

### Wave 0 — Stabilise (no folder move)
**Goal:** safe extractions that become features/shared later.

| ID | Task | Lands in (eventual) |
|----|------|---------------------|
| F0.1 | Clear sticky errors; loading vs empty; stale lens UX | `features/dashboard-query` later |
| F0.2 | Tests `withLensQuery` + `apiHttp` | `shared/api` |
| F0.3 | Extract `useDashboardLensQuery` (still under `hooks/` or `features/dashboard-query`) | `features/dashboard-query` |
| F0.4 | Extract `SortableDataTable` | `shared/ui` |

**Done when:** Skills/Rates/Languages use shared query + no P0 UX bugs.

### Wave 1 — Shared + Entities API foundation
**Goal:** FSD `shared` + `entities/*/api` without rewriting UI.

| ID | Task |
|----|------|
| F1.1 | Create `shared/api` (`http`, `query`); re-export from old paths if needed |
| F1.2 | Split façade → `entities/market`, `entities/relation`, `entities/quality`, `entities/job`, `entities/source`, `entities/research-intent`, `entities/assistant` (`api`+`model`) |
| F1.3 | Thin `lib/api.ts` barrel **or** deprecate in favour of `@/entities/*/api` + `@/shared/api` |
| F1.4 | `runSource` / ops credentials → `features/run-source` + `features/ops-credentials` using `shared/api` |
| F1.5 | Unify `CoverageNote` under `entities/coverage-note` |

**Done when:** no new code in fat `lib/api.ts`; entities own DTOs.

### Wave 2 — Features out of dashboard chrome
| ID | Task |
|----|------|
| F2.1 | Move `LensToggle` → `features/lens-toggle` |
| F2.2 | Move `CountryFilter` (+ boundary) → `features/country-filter` |
| F2.3 | Move prefs provider/panel → `features/dashboard-prefs` |
| F2.4 | `PeriodChip`, compare hints → features or shared as appropriate |
| F2.5 | Layout imports features only (no deep dashboard paths for chrome) |

**Done when:** widgets import lens/country/prefs via feature public APIs.

### Wave 3 — Widgets from `components/dashboard` & charts
| ID | Task |
|----|------|
| F3.1 | One analytics widget per route (`widgets/skills-dashboard`, …); page stays 5–15 lines |
| F3.2 | Peel ChartFrame table → `shared/ui`; charts primitives → `shared/ui/charts` |
| F3.3 | `useChartTopN`; GeoStrip→RankBars in shared |
| F3.4 | Split Executive into widget sections (&lt;250 orchestrator) |
| F3.5 | Relations stays composition-first (already closest to FSD widgets) |

**Done when:** `components/dashboard/` empty or shim re-exports only.

### Wave 4 — Remaining product widgets
| ID | Task |
|----|------|
| F4.1 | `research/*` → `widgets/*` + keep intent CRUD in `entities/research-intent` / features |
| F4.2 | `explorer/*` → `widgets/explorer` (+ shared URL parsers in `entities/job` or `shared/lib`) |
| F4.3 | `jobs/*` → `widgets/jobs-list`; optional RSC first page |
| F4.4 | Root ops → `widgets/sources-catalog`, `features/ops-credentials`, `entities/source` |
| F4.5 | Assistant → widgets + `entities/assistant` |

**Done when:** `components/` root has no feature files; only shims if needed.

### Wave 5 — Hardening
| ID | Task |
|----|------|
| F5.1 | Delete shims; fix deep imports |
| F5.2 | Steiger / ESLint import boundaries |
| F5.3 | Modular ECharts + GeoJSON vendor (`shared/ui/charts`) |
| F5.4 | Docs: ADR “Frontend adopts FSD” + update SPEC-ux-shell |

---

## 7. Dependency sketch (target)

```
app/[locale]/skills/page
        │
        ▼
widgets/skills-dashboard  ──► features/lens-toggle
        │                     features/country-filter
        │                     features/dashboard-prefs
        │                     features/dashboard-query
        ▼
entities/market (api+model)
        │
        ▼
shared/api + shared/ui (SortableDataTable, charts) + shared/hooks
```

---

## 8. What not to do

- Invent `processes/` layer  
- Let widgets import other widgets  
- Put API clients only in widgets (belongs in entities/features)  
- Move everything before Wave 0 bugfixes  
- Mix IT/CH source credential work into FSD PRs  
- Create a second Next `pages/` router — App Router stays  

---

## 9. Suggested calendar (~3 weeks)

| Days | Wave | Outcome |
|------|------|---------|
| 1–2 | 0 | P0 UX + query hook + table shell + API tests |
| 3–5 | 1 | Entities/shared API; thin barrel |
| 6–8 | 2 | Lens / country / prefs as features |
| 9–12 | 3 | Analytics widgets + ChartFrame peel |
| 13–15 | 4 | Jobs / sources / explorer / assistant |
| Flex | 5 | Lint boundaries + ADR + ECharts |

Each PR: **one wave slice**, smoke affected routes, keep `@/` shims until Wave 5.

---

## 10. Acceptance

- [ ] Layer folders exist: `widgets/`, `features/`, `entities/`, `shared/` (plus Next `app/`)  
- [ ] No cross-import between same-layer slices (spot-check + optional Steiger)  
- [ ] Analytics pages only import widgets + app providers  
- [ ] Market/job/source types live under `entities/*/model`, not duplicated in UI  
- [ ] `lib/api.ts` / `components/dashboard/` gone or shim-only  
- [ ] Smoke: home, skills, rates, trends, quality, relations, jobs, explorer, sources, assistant  

---

## 11. Relation to the quality plan

| Quality plan item | FSD home |
|-------------------|----------|
| P0 sticky error / empty flash | Wave 0 → later `features/dashboard-query` |
| Split `api.ts` | Wave 1 `entities/*` + `shared/api` |
| `useDashboardLensQuery` / shells | Wave 0–2 `features` + `widgets` |
| ChartFrame / ECharts | Wave 3 + 5 `shared/ui` |
| Catalog / credentials / jobs RSC | Wave 4 |

Quality work **is** the FSD migration fuel — every extract should land in the correct layer, not grow `components/dashboard` further.
