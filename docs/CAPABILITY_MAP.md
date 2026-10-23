# Capability Map: Freelance Market Intelligence

Stable module ids. Specs, plans, and tasks select work by these ids.

| Module id | Responsibility | Depends on |
|-----------|----------------|------------|
| sources | Global catalog (~193), verification statuses, coverage docs, catalog APIs | — |
| research-intents | Demand Compass: discovery watchlist + focus intents; lenses; LLM briefs; `query_id` provenance | — |
| ingest | Authorized/public collectors, ATS boards, file import, dedup, sync runs | sources, research-intents |
| classify | Rules / hybrid / LLM classification, taxonomy, evidence kinds | ingest |
| analytics | KPI summary, rates, countries, co-occurrence, trends, quality; `evidence_tier` + `min_evidence=standard` gates (skills/rates/trends/briefs); `coverage_notes` | classify |
| dashboard | Next.js UI IT/EN, chart-forward signal desk, guided vs trends-only, prefs | analytics, research-intents |
| profile-outcomes | User profile, skill gaps, applications, alerts, weekly report | analytics |
| ops | Config, API key, rate limit, scheduler, CI, logs, backups | ingest, classify, research-intents |
| mcp-analytics | MCP over DB metadata + semantic metrics → DashboardSpec/ReportSpec for LLM | analytics, ops, research-intents |
| rag-knowledge | Optional RAG over job text / imported docs (Later) | classify, ops |
| stats-ingest | Official labour/wage open data series (Later) | sources, ops |
| procurement | Public tenders as distinct entities from jobs (Later) | sources, ops |

## Build order

```
sources → research-intents → ingest → classify → analytics → dashboard → profile-outcomes → ops
         → mcp-analytics (after analytics stable; scope by intent when provided)
         → (later) rag-knowledge | stats-ingest | procurement
```

`dashboard` and `profile-outcomes` may proceed in parallel after `analytics` is stable.  
`research-intents` **shipped** (discovery + focus, daily crawlers, `job_intent_matches`, lenses `market`/`focus`/`compare`, Market scan / Focus UI, Explorer Refresh, Assistant brief chips + accept watches, MCP `render_demand_brief`); product sync no longer uses silent env topic defaults ([ADR-007](decisions/ADR-007-query-first-sync.md)). Ops walkthrough: [ops/demand-compass-walkthrough.md](ops/demand-compass-walkthrough.md); smoke: `backend/scripts/smoke_compass.sh` (+ CI `compass-smoke`).  
`dashboard` includes IT/EN (`next-intl`) + chart-forward Executive/Trends; `LensToggle` on Executive, Trends, Jobs, Skills, Quality (and Rates/Countries/Assistant). Assistant propose/briefs accept `locale` (`en`|`it`) and echo `meta.locale` / `meta.narrative_locale`; **narratives remain EN MVP** (IT narratives = Later). SPEC-i18n / SPEC-dashboard MVP acceptance signed off.  
`mcp-analytics` includes `render_demand_brief` alongside schema/spec tools.  
FX helpers (Frankfurter/ECB) live under ingest/sources support paths, not a separate product module.

## Interface notes

- **sources → ingest:** catalog keys, verification status, connector registration; only `ACTIVE`/`enabled` run collectors.
- **research-intents → ingest:** **daily crawlers** dump → discovery → focus; each search run passes `query_text` + `query_id`; no env topic defaults.
- **research-intents → dashboard:** Market scan + My focus UI; `LensToggle` on signal dashboards (incl. Jobs/Skills/Quality); Explore DB-first; Refresh explicit; Assistant brief chips + accept watches (`/assistant`).
- **research-intents → analytics / mcp-analytics:** `lens` + `query_ids` via `job_intent_matches`; LLM brief types (rising/cooling, geo, adjacent, compare, suggest watches + accept); assistant `locale` meta (narratives EN MVP).
- **ingest → classify:** normalized job rows + raw text fields for classification.
- **classify → analytics:** stored contract/remote/skills/rates with evidence metadata.
- **analytics → dashboard:** JSON API under `/api/v1/*` (see OpenAPI at `/docs`).
- **analytics → profile-outcomes:** same market queries + profile skill set for gaps.
- **analytics → mcp-analytics:** semantic metric catalog + safe reads; LLM returns validated specs, not raw SQL to the UI.
- **mcp-analytics → dashboard:** `DashboardSpec` applies to widgets/prefs (after customization); `ReportSpec` materializes via reports.
- **ops:** cross-cutting; owns **daily crawler** cron/tick + budgets; does not own domain topic strings.
- **rag-knowledge:** unstructured text Q&A; complementary to MCP structured composition.
- **stats-ingest / procurement (Later):** separate entities; never silently merge into job rate KPIs.

## Spec index

- [SPEC-sources.md](specs/SPEC-sources.md)
- [SPEC-research-intents.md](specs/SPEC-research-intents.md)
- [SPEC-ingest.md](specs/SPEC-ingest.md)
- [SPEC-classify.md](specs/SPEC-classify.md)
- [SPEC-analytics.md](specs/SPEC-analytics.md)
- [SPEC-dashboard.md](specs/SPEC-dashboard.md)
- [SPEC-i18n.md](specs/SPEC-i18n.md)
- Experience: [ideas/demand-compass-experience.md](ideas/demand-compass-experience.md)
- Visual/i18n plan: [superpowers/plans/2026-10-20-i18n-and-visual-dashboard.md](superpowers/plans/2026-10-20-i18n-and-visual-dashboard.md)
- [SPEC-profile-outcomes.md](specs/SPEC-profile-outcomes.md)
- [SPEC-ops.md](specs/SPEC-ops.md)
- [SPEC-mcp-analytics.md](specs/SPEC-mcp-analytics.md)
- Idea: [ideas/freelance-demand-compass.md](ideas/freelance-demand-compass.md)
- ADR: [decisions/ADR-007-query-first-sync.md](decisions/ADR-007-query-first-sync.md)
- Plan: [superpowers/plans/2026-10-20-query-first-daily-sync.md](superpowers/plans/2026-10-20-query-first-daily-sync.md)
- MCP plan: [superpowers/plans/2026-10-20-mcp-schema-dashboards.md](superpowers/plans/2026-10-20-mcp-schema-dashboards.md)
- RAG: [superpowers/plans/2026-10-20-rag-knowledge-layer.md](superpowers/plans/2026-10-20-rag-knowledge-layer.md) (no SPEC until prioritized)
- Global sources expansion: [superpowers/plans/2026-10-20-global-sources.md](superpowers/plans/2026-10-20-global-sources.md)
