# Spec: UX shell (Atlas)

**Status:** Accepted direction — 2026-10-21  
**Supersedes (visual naming only):** “signal desk” token nicknames in [SPEC-dashboard.md](SPEC-dashboard.md) remain valid; **Atlas** is the approved IA + visual language going forward.  
**Related:** [SPEC-dashboard.md](SPEC-dashboard.md) · [SPEC-i18n.md](SPEC-i18n.md) · [../ideas/demand-compass-experience.md](../ideas/demand-compass-experience.md)

## Objective

Give Freelance Market Intelligence a clearer **information architecture** (four nav zones) and a **distinctive, modern** UI foundation—cool slate + teal—without rewriting every page in one pass.

## Approved direction: Atlas

| Attribute | Choice |
|-----------|--------|
| Name | **Atlas** |
| Mood | Cool analytical desk; cartographic calm, not neon |
| Palette | Cool slate surfaces + teal accent (`--signal`) |
| Explicitly rejected | Purple/indigo gradients; warm cream + terracotta; broadsheet (hairline rules, zero radius, dense newspaper columns) |

## Information architecture — four zones

Primary chrome groups existing routes. Labels are localized (`nav.zone*`). Hrefs and prefs keys stay stable so `nav_hidden` and presets keep working.

| Zone | Purpose | Routes (href → nav key) |
|------|---------|-------------------------|
| **Explore** | Market overview & analytics | `/` executive · `/market-scan` marketScan · `/explorer` explorer · `/trends` trends · `/skills` skills · `/rates` rates · `/countries` countries |
| **Jobs** | Listings & personal pipeline | `/jobs` jobs · `/profile` profile · `/applications` applications |
| **Ops** | Data health & sources | `/quality` quality · `/sources` sources · `/alerts` alerts |
| **Research** | Intent-driven corpus & coaching | `/focus` myFocus · `/report` report · `/assistant` assistant |

Rules:

1. Zone labels are **grouping only** — they are not separate pages.
2. Direct URLs still work when an item is hidden via prefs.
3. Future routes must declare a zone in `frontend/lib/navZones.ts` before appearing in chrome.
4. Do **not** flatten zones back into a single unsorted pill row without a SPEC update.

## Design tokens (CSS variables)

Defined in `frontend/app/globals.css` on `:root` / `.dark`. Back-compat aliases `--bg`, `--fg`, `--accent` remain.

| Token | Role |
|-------|------|
| `--ink` | Primary text (slate) |
| `--paper` | Page ground |
| `--card` | Elevated surface |
| `--line` | Borders / dividers |
| `--muted` | Secondary text |
| `--signal` | Teal accent / primary actions / active chrome |
| `--rise` | Rising demand (emerald) |
| `--cool` | Cooling / geo / secondary series (sky) |
| `--warn` | Warnings / coverage gaps |
| `--font-display` / `--font-sans` / `--font-mono` | next/font CSS variables |
| `--display` / `--sans` / `--mono` | Font stacks used in CSS |

Light-first; optional `.dark`. Atmosphere may use **subtle** teal/sky radial washes on `--paper` — not purple blooms.

## Typography

Loaded via `next/font/google` in `app/[locale]/layout.tsx` (no render-blocking `<link>` to fonts.googleapis.com).

| Role | Font | Why |
|------|------|-----|
| Display / brand | **Syne** (600–700) | Geometric, distinctive; reads as product, not Inter/Roboto |
| UI body | **Source Sans 3** (400–700) | Neutral, highly legible for dense dashboards |
| Metrics / `n=` / code | **IBM Plex Mono** (400–500) | Already used for evidence counts; keep continuity |

Fallbacks: `ui-sans-serif` / `ui-monospace` system stacks. Prefer `font-family: var(--display)` on brand/tagline headings; body uses `var(--sans)`.

**Fontshare alternative (if Google fonts constrained later):** Satoshi (UI) + JetBrains Mono (metrics)—document swap in this SPEC before changing code.

## Component inventory

### Live / thin foundation (this slice)

| Piece | Location | Notes |
|-------|----------|-------|
| Atlas tokens | `app/globals.css` | CSS variables + utility classes (`.card`, `.signal-text`, …) |
| Fonts | `app/[locale]/layout.tsx` | next/font variables on `<html>` |
| Zoned nav | `lib/navZones.ts` + `AppChrome` | Four zone groups; pills retained for minimal churn |
| Prefs hide-nav | `PrefsPanel` + `NAV_ITEMS` | Flat list derived from zones |

### Existing product UI (restyle later; not required this slice)

| Piece | Location |
|-------|----------|
| Executive / charts | `components/dashboard/*`, `components/charts/*` |
| Jobs table | `components/jobs/JobsListDashboard.tsx` |
| Pagination control | `components/jobs/JobsPagination.tsx` (**shipped** — wired into `JobsListDashboard`) |
| Explorer / research | `app/[locale]/explorer`, `components/research/*` |
| Assistant / Compass | `components/assistant/*` |

### Deferred (shadcn / Radix)

**shadcn/ui is not installed** (`package.json` has Tailwind + `clsx` + TanStack Table; no Radix, no `class-variance-authority`, no `tailwind-merge`).

Prefer **tokens + IA first**. When adding Button/Table primitives:

```bash
cd frontend
npx shadcn@latest init
# choose: style default, base color slate, CSS variables yes, RSC yes
npx shadcn@latest add button table
```

Minimal manual deps if CLI unavailable:

- `@radix-ui/react-slot`
- `class-variance-authority`
- `tailwind-merge`
- keep existing `clsx`

Map Atlas tokens into shadcn’s CSS variable scheme (`--primary` → `--signal`, `--background` → `--paper`, `--foreground` → `--ink`, `--border` → `--line`) so components inherit Atlas without a second palette.

Do **not** migrate every page to shadcn in one PR.

## Pagination pattern

Canonical pattern for long tables/lists:

1. **Server-aware page state:** `page` (1-based) + fixed `pageSize` (default 25–50; Jobs may use 100).
2. **API:** `limit` + `offset` (or equivalent) from `(page - 1) * pageSize`.
3. **UI:** reuse `JobsPagination` — range text (`showingRange`), prev/next, `pageOf`, `aria-label` from i18n.
4. **Evidence:** always show observed `total` / `n=` in mono; never invent market size.
5. **Empty:** zone-appropriate empty copy + links into Explore / Research (see SPEC-dashboard empty states).

**Shipped:** `JobsPagination` is wired into `JobsListDashboard` (server-aware `page` / `pageSize`, prev/next, i18n range). Keep it as the canonical reference for other long lists. Full Jobs table restyle and shadcn primitives remain deferred (below).

## Out of scope (this SPEC / foundation slice)

- Full visual redesign of Executive, Trends, charts, or every route.
- Installing/migrating the whole app to shadcn.
- Changing API KPI semantics or analytics contracts.
- Sidebar collapse / mobile drawer (may come later; current chrome is top nav).

## Acceptance criteria

### SPEC & IA

- [x] Atlas approved as the named direction in this document.
- [x] Four zones defined with stable href mapping.
- [x] Chrome shows zone labels grouping links (Explore / Jobs / Ops / Research).
- [x] Prefs “hide nav” still lists all items; hidden items omit from chrome.

### Visual foundation

- [x] `:root` / `.dark` expose Atlas tokens (slate + teal); no purple primary.
- [x] Layout loads Syne + Source Sans 3 + IBM Plex Mono via `next/font`.
- [x] Brand/tagline uses display font; body uses sans; metrics can use `--mono`.
- [x] Existing pages still render under `AppChrome` without per-page rewrites.

### Process

- [x] shadcn install steps documented here; not forced in this slice.
- [x] File size for new/edited modules stays under 500 lines.
- [x] No git commit required for this foundation slice.

## Verification (local)

```bash
# from repo root — stack + frontend
docker compose up -d   # or existing compose relaunch script
# or frontend only:
cd frontend && npm run dev
```

1. Open `http://127.0.0.1:3000` (or locale-prefixed URL).
2. Confirm header nav shows **four zone labels** with links underneath.
3. Confirm brand uses Syne-like geometric display; body is Source Sans 3.
4. Confirm accent/active controls are **teal**, surfaces **cool slate** (not purple, not cream).
5. Toggle Prefs → hide a nav item → item disappears from chrome; zone may still show if siblings remain.
6. `npm run build` in `frontend/` succeeds.

## Build order (follow-ups)

1. Shared Jobs table styles (pagination UI already shipped).
2. Optional shadcn `button` / `table` mapped to Atlas tokens.
3. Progressive restyle of Explore pages (Executive → Trends → Explorer).
4. Mobile nav (overflow / drawer) if pill wrap becomes unusable.
