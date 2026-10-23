# Idea: Demand Compass experience (i18n + visual UX)

**Status:** adopted — core shipped (next-intl + chart kit); assistant `locale` polish remaining  
**Date:** 2026-10-20  
**Related:** [SPEC-i18n.md](../specs/SPEC-i18n.md), [SPEC-dashboard.md](../specs/SPEC-dashboard.md), [plan](../superpowers/plans/2026-10-20-i18n-and-visual-dashboard.md)

## Problem statement

How might FMI feel like a **premium signal desk** for freelancers—clear in **Italian and English**, with **gorgeous, readable charts**—so the Demand Compass (rising/cooling, where, focus vs market) is understood in seconds, not after scrolling tables?

## Recommended direction

### 1. Bilingual product (IT + EN)

- UI chrome, empty states, guided copy, assistant brief labels: **it** | **en**.
- Locale in prefs (`locale`), URL prefix optional (`/it/...`, `/en/...`) or cookie + `html lang`.
- Default: browser language if `it*` else `en`; user override sticky.
- LLM briefs and report titles respect locale; **numbers/ISO codes stay locale-neutral** (evidence first).
- Job source text stays original language; UI labels around it are translated.

### 2. Visual system — “Signal desk” (not generic AI dashboard)

Evolve the existing teal/Plex base into a sharper identity:

| Token | Intent |
|-------|--------|
| Ink `#0B1220` | Depth, authority |
| Signal teal `#0F766E` → chart series primary | Continuity with current accent |
| Rise amber `#D97706` | Rising demand |
| Cool slate `#64748B` | Cooling / flat |
| Paper wash | Soft radial wash (already present)—keep light-first; dark optional |
| Type | **IBM Plex Sans** UI + **IBM Plex Mono** for `n=`, deltas, IDs (already loaded)—add a single display weight for the product name “FMI / Demand Compass” |
| Motion | Lens crossfade, chart series draw-in (~300ms), KPI value tick—no decorative particle noise |

**Avoid:** purple neon, cream+terracotta serif kit, dense newspaper grids, emoji status, pill-stat spam in the first viewport.

### 3. Executive as one composition

First viewport of Executive (Demand Compass home):

1. Brand mark + lens control (Market / Focus / Compare) + locale
2. One sentence status (“Observed demand signals · last crawl … · n=…”)
3. **Hero chart:** rising vs cooling technologies (slope or diverging bars)
4. One CTA group: Ask assistant brief · Manage focus · Open trends

Below fold: geo strip, rates pulse, crawl health—not competing heroes.

### 4. Chart kit (ECharts — already in `package.json`)

| Chart | Where |
|-------|--------|
| Rising/cooling slope or butterfly | Executive, Trends |
| Sparkline strip (jobs/day) | Executive KPI row |
| Stacked/remote mix donut (small) | Countries / Executive aside |
| Compare dual-line (market vs focus) | Compare lens |
| Co-occurrence chord or heatmap (lite) | Skills (progressive) |
| Rate violin/box (observed only) | Rates |

Every chart: period, `n=`, empty/thin-sample state, export PNG optional Later.

### 5. UX principles

- **DB-first honesty:** empty = beautiful empty state with “next daily crawler”, never fake charts.
- **Progressive disclosure:** guided mode shows methodology in drawers, not walls of text.
- **Touch targets & a11y:** WCAG 2.2 AA contrast; charts have text alternatives / data tables toggle.
- **Density modes:** guided (airier) vs trends_only (dense signal)—same visual language.

## MVP scope

- `next-intl` (or equivalent) with `it`/`en` message catalogs for chrome + Executive/Trends/Explorer/Assistant.
- Design tokens in CSS variables; Executive hero chart + sparkline strip live.
- Locale toggle in chrome; prefs persist `locale`.
- Compare lens dual-series chart.

## Not doing (this slice)

- Full translation of every historical job description.
- 10+ locales.
- 3D/WebGL vanity charts.
- Redesigning backend KPI semantics.
