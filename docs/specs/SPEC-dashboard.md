# Spec: dashboard

**Status:** Accepted (MVP) — 2026-10-20  
Visual / i18n intent: [../ideas/demand-compass-experience.md](../ideas/demand-compass-experience.md) · [SPEC-i18n.md](SPEC-i18n.md).

## Objective

Provide a **beautiful, bilingual (IT/EN), chart-forward** Next.js UI over analytics APIs—the Demand Compass “signal desk”—with **guided** (evidence + methodology) and **trends_only** (dense charts, minimal coaching) presentation modes.

## In scope

- Pages: Executive, Explorer, Trends, Skills, Rates, Countries, Jobs, Quality, Sources (+ Profile/Applications/Alerts/Report owned with profile-outcomes).
- **Demand Compass UI:** Market scan (discovery) + My focus intents; lens toggle `market|focus|compare` on Executive/Trends ([SPEC-research-intents.md](SPEC-research-intents.md)).
- **Locale IT/EN** chrome + chart labels ([SPEC-i18n.md](SPEC-i18n.md)).
- **Graphic dashboards:** ECharts-based rising/cooling hero, sparklines, geo strip, compare dual-series (see § Visual system).
- **Explorer:** DB-first search; secondary **Refresh from sources**—no hardcoded “java” placeholder.
- **Assistant brief chips:** rising/cooling, where demand, adjacent, focus-vs-market, suggest watches (accept to persist)—labels localized.
- **Skills / Rates / Countries / Sources** as today, restyled to the signal-desk system.
- `view_mode`: `guided` | `trends_only` (default `guided`).
- Preferences: period, widgets, focus filters, nav hide, presets, **`locale`**, sticky analytics **`lens`**.
- Persistence: localStorage (bump version for locale); profile API sync when available.

## Out of scope (this module)

- Changing API KPI semantics (analytics owns numbers).
- RAG chat UI (rag-knowledge).
- Translating raw job posting text.
- WebGL/3D vanity visualizations.

## Modes

### Guided

- Show disclaimer, definition, limits, evidence badges, growth status.
- Show skill-gap / positioning recommendations when data exists.
- Methodology-oriented copy allowed.

### Trends-only

- Show metric values, tables, and charts for observed trends.
- **Must not show:** long disclaimer blocks, per-KPI definition/limits paragraphs, positioning recommendations, “guidelines” coaching copy.
- **May show:** short title, period label, `n=` sample size.
- Data still evidence-first (no invented totals).

## Customization acceptance

- [x] User can toggle `view_mode` and see Executive/Trends update without reload of backend data model.
- [x] User can hide nav items; hidden routes are not linked (direct URL may still work).
- [x] User can set `period_days` and focus filters used by list/summary fetches.
- [x] User can save/load at least one named preset.
- [x] Preferences survive refresh (localStorage `fmi:dashboardPrefs:v2`, migrates v1).
- [x] Sticky `lens` (`market`|`focus`|`compare`) survives refresh and is included in named presets / profile prefs; URL `?lens=` seeds on entry.
- [x] In `trends_only`, Executive does not render definition/limits/recommendation sections.

## Assistant acceptance

- [x] `/assistant` proposes DashboardSpec/ReportSpec via `POST /api/v1/assistant/propose`.
- [x] Apply DashboardSpec updates prefs (period, view_mode, focus filters).
- [x] Propose + Demand Compass briefs pass UI `locale`; API echoes `meta.locale` / `meta.narrative_locale`.
- [x] **MVP:** evidence narratives remain English (`narrative_locale=en`) — see [SPEC-i18n.md](SPEC-i18n.md).

## Sources UI acceptance

- [x] Sources page lists DB sources and can trigger enabled collectors.
- [x] Catalog / verification status visible (API and/or UI); credential-needed sources not presented as integrated.
- [x] Filter catalog by category/status in UI (`CatalogBrowser`).

## Demand Compass / Explorer acceptance

- [x] User can manage Market scan (discovery) and My focus intents separately. *(`/market-scan`, `/focus`)*
- [x] Executive/Trends default to lens=`market`; Focus/Compare available. *(`LensToggle` `DEFAULT_LENS="market"`)*
- [x] Explorer primary action searches Postgres only; Refresh is explicit. *(`ExplorerRefresh`)*
- [x] Search box does not default to a hardcoded profession string. *(`explorer/page.tsx`: `q` from URL only)*
- [x] Warn when too few discovery probes are enabled. *(`DiscoveryCoverageWarn` soft min 3; `MarketCoverageBanner` on dashboards)*
- [x] Empty state explains discover → focus → decide. *(jobs/explorer `emptyHint` + Market scan / My focus links; decide = Executive/Assistant, no dedicated page)*

## Visual system (“signal desk”)

### Design tokens (CSS variables)

| Token | Role |
|-------|------|
| `--ink`, `--paper`, `--card`, `--line` | Structure |
| `--signal` (teal) | Primary series / accents |
| `--rise` (amber) | Rising demand |
| `--cool` (slate) | Cooling / flat |
| `--mono` | IBM Plex Mono for `n=`, deltas |

Light-first; optional `.dark`. Avoid purple neon, cream+terracotta kits, broadsheet density.

### Typography & motion

- UI: IBM Plex Sans; mono for metrics; product name treated as brand-level in Executive header.
- Motion (min 2): lens switch crossfade; chart series enter; optional KPI tick. `prefers-reduced-motion` → instant.

### Chart inventory (ECharts — dependency already present)

| ID | Chart | Placement |
|----|-------|-----------|
| `rise_cool` | Slope or diverging bars rising vs cooling | Executive hero, Trends |
| `jobs_spark` | Sparkline jobs/day | Executive KPI strip |
| `geo_strip` | Horizontal bar or simple map-lite top countries | Executive / Countries |
| `compare_dual` | Dual line market vs focus | Compare lens |
| `remote_mix` | Compact donut remote/hybrid/onsite | Countries aside |
| `rates_box` | Box/percentile (NULL excluded) | Rates |
| `cooccur_heat` | Heatmap or top-pairs bars | Skills (phase 2 OK) |

Rules for every chart:

- Show period + `n=` + thin-sample / empty crawler state (localized).
- Provide “View as table” toggle for a11y.
- No invented series when `n` below analytics thresholds.
- Dynamic import of ECharts wrappers (bundle size).

### Executive first viewport (composition)

1. Brand (FMI / Demand Compass) + locale + lens + view_mode  
2. One status line (last crawl, lens, `n=`)  
3. Hero `rise_cool` chart  
4. CTA: Assistant brief · My focus · Trends  

No card grid of unrelated stats above the hero chart.

## i18n acceptance

- [x] IT and EN message catalogs cover chrome + Executive + Trends + Explorer + Assistant + chart chrome. *(294 keys parity 2026-10-20)*
- [x] Locale toggle persists in prefs; `<html lang>` updates.
- [x] See [SPEC-i18n.md](SPEC-i18n.md) for full criteria — **Accepted (MVP) 2026-10-20**.

## Visual / chart acceptance

- [x] Executive hero chart renders from real `technology_trends` (or empty/thin state). *(`RiseCoolChartLazy`)*
- [x] Compare lens shows `compare_dual` when focus matches exist; otherwise localized unavailable copy. *(`CompareDualLazy` + `compareReady` gate on Executive/Trends — series empty until `job_intent_matches` rematch populates focus half)*
- [x] Sparkline jobs/day on Executive below hero (or immediately adjacent on wide screens). *(`SparklineLazy` ← `summary.jobs_per_day`; empty/thin via `charts.empty` / `charts.thinSample` when n=0 or sparse)*
- [x] Geo strip present on Executive below hero (or immediately adjacent on wide screens). *(`GeoStripLazy` ← `summary.top_countries`)*
- [x] `trends_only` keeps charts, drops methodology walls.
- [x] Reduced-motion respected in chart kit (`chartTheme`); light-first tokens for text on washes. *(formal contrast audit Later)*

### Chart inventory residual (not MVP blockers)

| ID | Status |
|----|--------|
| `rise_cool`, `geo_strip`, `compare_dual`, `jobs_spark` | Shipped (ECharts lazy wrappers; compare data depends on focus matches; sparkline from `jobs_per_day`) |
| `remote_mix`, `rates_box` | Still table/card UI on Countries/Rates — dedicated charts Later |
| `cooccur_heat` | Skills co-occurrence table OK for phase 2 |

**Complete cockpit (Draft):** KPI catalog, world map, language requirements, facets — [SPEC-dashboard-charts.md](SPEC-dashboard-charts.md) · plan [../superpowers/plans/2026-10-22-complete-chart-dashboard.md](../superpowers/plans/2026-10-22-complete-chart-dashboard.md).

## Acceptance notes (2026-10-20)

Demand Compass UX, LensToggle (default market), Explorer DB-first, coverage banners, i18n chrome, and Executive/Trends chart kit (`rise_cool`, `geo_strip`, `compare_dual`, `jobs_spark`) match shipped code. SPEC-i18n MVP is **Accepted**. Visual checklist MVP is complete for chart wiring. Compare dual UI is done; live dual series still needs focus-match rematch data. Ops manual walkthrough (IT/EN toggle + live trends hero) remains a nice-to-have confirmation.

## Key paths

- `frontend/app/`
- `frontend/messages/{en,it}.json`
- `frontend/components/charts/` (ECharts wrappers)
- `frontend/components/dashboard/`
- `frontend/app/globals.css` (tokens)
- Product: [../PRODUCT.md](../PRODUCT.md)
- Experience idea: [../ideas/demand-compass-experience.md](../ideas/demand-compass-experience.md)
- i18n: [SPEC-i18n.md](SPEC-i18n.md)
- Research intents: [SPEC-research-intents.md](SPEC-research-intents.md)
- ADR: [../decisions/ADR-004-dashboard-modes.md](../decisions/ADR-004-dashboard-modes.md), [../decisions/ADR-007-query-first-sync.md](../decisions/ADR-007-query-first-sync.md)
- Plans: [../superpowers/plans/2026-10-20-i18n-and-visual-dashboard.md](../superpowers/plans/2026-10-20-i18n-and-visual-dashboard.md), [../superpowers/plans/2026-10-20-dashboard-customization.md](../superpowers/plans/2026-10-20-dashboard-customization.md), [../superpowers/plans/2026-10-20-query-first-daily-sync.md](../superpowers/plans/2026-10-20-query-first-daily-sync.md)
