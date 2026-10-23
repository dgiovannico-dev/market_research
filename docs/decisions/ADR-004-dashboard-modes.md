# ADR-004: Dashboard modes (guided vs trends-only) and customization

## Status

Accepted

## Date

2026-10-20

## Context

Some users want methodology, skill-gap coaching, and evidence badges. Others want a clean dashboard that only shows trends—without guidelines, long disclaimers, or recommendations. The product must be customizable for both.

## Decision

Introduce a user preference `view_mode`:

- `guided` (default): evidence copy, definitions, limits, recommendations.
- `trends_only`: minimal presentation—tables/charts of observed trends; no guideline/recommendation panels; short labels + optional `n=` only.

Also support customization of widgets, period, focus filters, nav visibility, named presets, and **`locale` (`it` | `en`)**. Persist in versioned `localStorage`; optionally sync to profile later.

Presentation follows the **signal-desk** visual system (chart-forward Executive, ECharts kit, IT/EN copy)—see [SPEC-dashboard.md](../specs/SPEC-dashboard.md), [SPEC-i18n.md](../specs/SPEC-i18n.md). Modes change coaching density, not chart honesty.

Analytics APIs remain evidence-first in both modes; mode and locale are **presentation** concerns (dashboard module).

## Alternatives considered

### Single guided UI only

- Pros: one layout
- Cons: rejects power-user “just show trends” need
- Rejected

### Separate apps

- Pros: hard separation
- Cons: duplicate maintenance
- Rejected

### Strip evidence from APIs in trends mode

- Pros: smaller payloads
- Cons: couples API to UI preference; harder for exports
- Rejected; filter in UI (and optional query flag later if needed)

## Consequences

- SPEC-dashboard and PRODUCT.md define acceptance.
- Implementation plan: `docs/superpowers/plans/2026-10-20-dashboard-customization.md`.
- Profile/report recommendation UIs respect `view_mode` when embedding on Executive.
