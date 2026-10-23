# Dashboard Customization Implementation Plan

> **For agentic workers:** Implement task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship customizable dashboards with `guided` and `trends_only` view modes.

**Architecture:** Client-side preference store (versioned localStorage v2) drives conditional rendering on Executive/Trends and nav visibility. Analytics APIs unchanged; presentation-only mode per ADR-004.

**Tech Stack:** Next.js App Router, TypeScript, existing `frontend/lib/api.ts`

**Spec:** [docs/specs/SPEC-dashboard.md](../../specs/SPEC-dashboard.md), [docs/PRODUCT.md](../../PRODUCT.md), [docs/decisions/ADR-004-dashboard-modes.md](../../decisions/ADR-004-dashboard-modes.md)

## Global Constraints

- File size ≤ 500 lines; extract prefs hook/module if needed.
- Evidence-first: never invent market totals in trends-only.
- No new secrets.

## Review Focus

- Trends-only must not leak recommendation panels via shared layout components.
- localStorage quota / private mode: fail soft to defaults.
- Preset apply must be atomic (all-or-nothing preference replace).
- Hidden nav must not break deep links.
- Period/focus filters must match API query params already supported.

---

### Task 1: Preferences module

**Files:**
- Create: `frontend/lib/dashboardPrefs.ts`
- Test: manual + optional unit if vitest added later

**Steps:**
- [x] Define `DashboardPrefs` type (`view_mode`, `period_days`, `visible_widgets`, `focus_technologies`, `focus_countries`, `nav_hidden`, `presets`)
- [x] Versioned key `fmi:dashboardPrefs:v2` (migrates v1); load/save with try/catch
- [x] Defaults: `view_mode=guided`, `period_days=30`
- [x] Commit *(landed in prior work; do not re-commit unless asked)*

---

### Task 2: Prefs provider + mode toggle UI

**Files:**
- Create: `frontend/components/DashboardPrefsProvider.tsx` (or equivalent)
- Modify: `frontend/app/layout.tsx`

**Steps:**
- [x] Client provider exposing prefs + `setPrefs` / `applyPreset`
- [x] Compact toggle Guided | Trends-only in header
- [x] Persist on change
- [x] Commit *(prior work)*

---

### Task 3: Trends-only Executive + Trends

**Files:**
- Modify: `frontend/app/page.tsx`
- Modify: `frontend/app/trends/page.tsx`
- Possibly extract presentational pieces under `frontend/components/dashboard/`

**Steps:**
- [x] When `trends_only`, omit disclaimer, definition, limits, recommendation sections
- [x] Keep titles, values, `n=`, tables/charts
- [x] Manual check both modes
- [x] Commit *(prior work)*

---

### Task 4: Nav hide + focus filters + presets

**Files:**
- Modify: `frontend/app/layout.tsx`
- Modify: explorer/jobs fetch call sites as needed
- Create: `frontend/components/PrefsPanel.tsx` (settings drawer)

**Steps:**
- [x] Filter nav by `nav_hidden` (includes Market scan + My focus)
- [x] Wire `period_days` / focus into summary and jobs queries
- [x] Save/load named preset
- [x] `npm run build`
- [x] Commit *(prior work)*

---

### Task 5: Persist analytics lens in prefs + presets

**Files:**
- Modify: `frontend/lib/dashboardPrefs.ts`
- Modify: `frontend/components/dashboard/LensToggle.tsx`
- Modify: `frontend/components/dashboard/PrefsPanel.tsx` (profile merge)

**Steps:**
- [x] Add `lens` to `DashboardPrefs` (default `market`); normalize on load
- [x] `LensToggle` writes sticky prefs on change; URL `?lens=` seeds once on entry
- [x] Named presets / profile pull-push include `lens`; applying a preset restores URL
- [x] Verify: Focus → refresh → still Focus; save preset with Compare → load restores Compare

## Checkpoint

- [x] Guided mode still shows evidence copy
- [x] Trends-only has no guidelines/recommendations
- [x] Prefs survive refresh
- [x] Build green
- [x] Lens survives refresh / named presets
