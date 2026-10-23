# Plan: i18n (IT/EN) + visual Demand Compass dashboards

> **For agentic workers:** Implement task-by-task. Keep files ≤500 lines. Dynamic-import ECharts. No fake chart data. Follow signal-desk tokens (no purple/cream cliché kits).

**Goal:** Bilingual IT/EN UI + gorgeous chart-forward Executive/Trends that make rising/cooling, geo, and compare lenses obvious at a glance.

**Specs:** [SPEC-i18n.md](../../specs/SPEC-i18n.md) · [SPEC-dashboard.md](../../specs/SPEC-dashboard.md) · [idea](../../ideas/demand-compass-experience.md)

**Stack:** Next.js App Router, `next-intl`, ECharts (`echarts` + `echarts-for-react` already in `frontend/package.json`), Tailwind, existing prefs provider.

---

## File map

| Area | Paths |
|------|--------|
| Locales | `frontend/messages/en.json`, `it.json`; `app/[locale]/…` or middleware |
| Tokens | `frontend/app/globals.css` |
| Charts | `frontend/components/charts/*` |
| Executive | `frontend/components/dashboard/ExecutiveDashboard*` (split if >500 lines) |
| Prefs | locale field + key bump |
| Assistant | pass `locale` to propose API |

---

### Task 1: Design tokens + chrome polish

Update CSS variables (`--signal`, `--rise`, `--cool`, …). Refine `AppChrome` spacing, brand treatment, lens control styling. No layout logic change yet.

### Task 2: `next-intl` skeleton

- Add dependency; `[locale]` segment or middleware.
- Message files; parity test script (key diff en/it).
- Wire layout `lang`; locale toggle → prefs.

### Task 3: Translate MVP surfaces

Migrate strings: nav, Executive, Trends, Explorer, Assistant, empty/crawl states, prefs. Leave job body text untouched.

### Task 4: Chart primitives

Create thin wrappers (dynamic import):

- `RiseCoolChart`, `Sparkline`, `GeoStrip`, `CompareDual`
- Shared: period/`n=` footer, table toggle, empty/thin states (i18n keys)
- Theme colors from CSS variables

### Task 5: Executive composition

Rebuild first viewport per SPEC-dashboard: brand + lens + locale + status → hero `rise_cool` → CTAs → sparkline/geo. Guided methodology in collapsible drawer.

### Task 6: Trends + Compare

Trends page uses same chart kit denser. Compare lens mounts `CompareDual` when focus data exists.

### Task 7: Assistant locale

Pass `locale` into propose/briefs; chip labels from messages.

### Task 8: Verify

- `npm run build`
- Key parity en/it
- Manual IT/EN + reduced-motion + empty crawler state
- No chart without `n=` disclosure

---

## Done when

- [x] Core SPEC-i18n / visual paths landed (`next-intl`, `en`/`it` parity, Executive/Trends chart kit).
- [x] Formal SPEC checkbox sign-off — [SPEC-i18n.md](../../specs/SPEC-i18n.md) **Accepted (MVP)** + [SPEC-dashboard.md](../../specs/SPEC-dashboard.md) Demand Compass / i18n / visual checklists (2026-10-20).
- [x] Executive hero chart live from API (or honest empty) — `RiseCoolChart` / compare dual on Executive
- [x] Locale sticky across refresh — prefs `locale` + chrome toggle → `[locale]` routes
- [x] Assistant propose/briefs pass `locale` (meta echo; **`narrative_locale=en` MVP** — no Italian narrative generation)

## Verification notes

| Area | Evidence | Status |
|------|----------|--------|
| Tokens + chrome | `globals.css` / Tailwind `signal`/`rise`/`cool` | Done |
| next-intl skeleton | `app/[locale]`, `messages/{en,it}.json` | Done |
| Chart primitives | `frontend/components/charts/*` + `lazy.tsx` | Done |
| Message key parity | 294 keys en ↔ it (checked 2026-10-20) | Done |
| Assistant `locale` | propose/brief body + `meta` echo; FE `useLocale()` | Done (narrative EN MVP) |
| SPEC acceptance | SPEC-i18n + SPEC-dashboard checklists | Signed off 2026-10-20 |

## Out of scope

- Demand Compass backend crawlers (separate plan — **core shipped**; see query-first plan)
- Extra locales, 3D charts, translating job posts
