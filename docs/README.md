# Freelance Market Intelligence — Documentation

Evidence-first market intelligence for IT freelancers. Counts always mean **observed records in this database**, never invented total market size. Global source candidates (~193) are tracked honestly; only verified connectors are `ACTIVE`.

## Start here

| Doc | Purpose |
|-----|---------|
| [PRODUCT.md](PRODUCT.md) | Vision, persona, priority roles, global sources rules, guided vs trends-only |
| [CAPABILITY_MAP.md](CAPABILITY_MAP.md) | Stable modules, dependencies, build order |
| [SPEC.md](SPEC.md) | Master engineering spec (commands, structure, testing, boundaries) |
| [ROADMAP.md](ROADMAP.md) | Now / Next / Later |
| [PRODUCTION.md](PRODUCTION.md) | Runtime hardening, security, verification |
| [ops/demand-compass-walkthrough.md](ops/demand-compass-walkthrough.md) | Demand Compass UI ops path + `smoke_compass.sh` |
| [GLOSSARY.md](GLOSSARY.md) | Ubiquitous language (evidence, lenses, connectors, intents) |
| [ops/connector-alignment.md](ops/connector-alignment.md) | Catalog / registry / DB connector triple-truth checklist |

## Module specs

| Spec | Module |
|------|--------|
| [specs/SPEC-sources.md](specs/SPEC-sources.md) | Global catalog, verification statuses, procedure |
| [specs/SPEC-research-intents.md](specs/SPEC-research-intents.md) | User queries drive corpus; no silent topic defaults |
| [specs/SPEC-ingest.md](specs/SPEC-ingest.md) | Collectors, ATS, import, dedup, FX helpers |
| [specs/SPEC-classify.md](specs/SPEC-classify.md) | Rules / hybrid / LLM, evidence model |
| [specs/SPEC-analytics.md](specs/SPEC-analytics.md) | KPI, rates, countries, co-occurrence, trends, combo demand |
| [specs/SPEC-dashboard.md](specs/SPEC-dashboard.md) | Signal-desk UI, charts, Sources, prefs, trends-only |
| [specs/SPEC-ux-shell.md](specs/SPEC-ux-shell.md) | Atlas IA (4 zones), tokens, typography, shadcn plan |
| [specs/SPEC-i18n.md](specs/SPEC-i18n.md) | Italian & English UI / assistant locale |
| [specs/SPEC-profile-outcomes.md](specs/SPEC-profile-outcomes.md) | Profile, applications, alerts, weekly report |
| [specs/SPEC-ops.md](specs/SPEC-ops.md) | Auth, rate-limit, scheduler, CI, observability |
| [specs/SPEC-mcp-analytics.md](specs/SPEC-mcp-analytics.md) | MCP metadata tools → dashboard/report specs |

## Decisions (ADRs)

| ADR | Topic |
|-----|--------|
| [decisions/ADR-001-evidence-first-kpis.md](decisions/ADR-001-evidence-first-kpis.md) | Observed ≠ market size |
| [decisions/ADR-002-classification-modes.md](decisions/ADR-002-classification-modes.md) | rules / hybrid / llm |
| [decisions/ADR-003-authorized-connectors-only.md](decisions/ADR-003-authorized-connectors-only.md) | No ToS-bypass scraping; ACTIVE gate |
| [decisions/ADR-004-dashboard-modes.md](decisions/ADR-004-dashboard-modes.md) | Guided vs trends-only + prefs |
| [decisions/ADR-005-global-source-catalog.md](decisions/ADR-005-global-source-catalog.md) | Catalog as system of record |
| [decisions/ADR-006-mcp-schema-driven-analytics.md](decisions/ADR-006-mcp-schema-driven-analytics.md) | MCP + validated specs, not free SQL UI |
| [decisions/ADR-007-query-first-sync.md](decisions/ADR-007-query-first-sync.md) | Discovery + focus sync; no silent topic defaults |
| [decisions/ADR-008-hexagonal-ddd-incremental.md](decisions/ADR-008-hexagonal-ddd-incremental.md) | Hexagonal + DDD ports-first; no entity big-bang |

## Ideas

| Idea | Focus |
|------|--------|
| [ideas/freelance-demand-compass.md](ideas/freelance-demand-compass.md) | Discovery + focus corpus; LLM evidence coach for freelancers |
| [ideas/demand-compass-experience.md](ideas/demand-compass-experience.md) | IT/EN + chart-forward signal-desk UX |
| [ideas/query-first-research-corpus.md](ideas/query-first-research-corpus.md) | Superseded draft (confirmation-bias fix documented) |

## Implementation plans

| Plan | Focus |
|------|--------|
| [superpowers/plans/2026-10-20-query-first-daily-sync.md](superpowers/plans/2026-10-20-query-first-daily-sync.md) | Demand Compass: discovery + focus sync, lenses, LLM briefs |
| [superpowers/plans/2026-10-20-i18n-and-visual-dashboard.md](superpowers/plans/2026-10-20-i18n-and-visual-dashboard.md) | IT/EN + ECharts Executive/Trends visual polish |
| [superpowers/plans/2026-10-20-global-sources.md](superpowers/plans/2026-10-20-global-sources.md) | Catalog deliverables + credentialed expansion |
| [superpowers/plans/2026-10-20-dashboard-customization.md](superpowers/plans/2026-10-20-dashboard-customization.md) | Custom prefs + trends-only UI |
| [superpowers/plans/2026-10-20-mcp-schema-dashboards.md](superpowers/plans/2026-10-20-mcp-schema-dashboards.md) | MCP schema → LLM dashboards/reports |
| [superpowers/plans/2026-10-20-production-hardening.md](superpowers/plans/2026-10-20-production-hardening.md) | Multi-node ops, metrics, secrets |
| [superpowers/plans/2026-10-20-rag-knowledge-layer.md](superpowers/plans/2026-10-20-rag-knowledge-layer.md) | Optional RAG over jobs/docs |
| [superpowers/plans/2026-10-23-backend-hexagonal-ddd.md](superpowers/plans/2026-10-23-backend-hexagonal-ddd.md) | Backend Hexagonal + DDD waves |

## Reviews

| Review | Focus |
|--------|--------|
| [reviews/2026-10-20-demand-compass-tech-review.md](reviews/2026-10-20-demand-compass-tech-review.md) | Demand Compass proposal vs codebase; must-fix gaps |

## Agent execution

| File | Purpose |
|------|---------|
| [../tasks/plan.md](../tasks/plan.md) | Execution overview for agents |
| [../tasks/todo.md](../tasks/todo.md) | Ordered vertical tasks with acceptance criteria |

## Global sources

| Doc | Purpose |
|-----|---------|
| [sources/README.md](sources/README.md) | Catalog API + regenerate + categories |
| [sources/VALIDATION_REPORT.md](sources/VALIDATION_REPORT.md) | Probe evidence / ACTIVE connectors |
| [sources/COVERAGE_GAPS.md](sources/COVERAGE_GAPS.md) | Geographic & professional gaps |
| [`data/sources/catalog.json`](../data/sources/catalog.json) | Full ~193-source registry |

## MCP (planned)

| Doc | Purpose |
|-----|---------|
| [mcp/CURSOR.md](mcp/CURSOR.md) | Cursor wiring (after implementation) |
| [specs/SPEC-mcp-analytics.md](specs/SPEC-mcp-analytics.md) | Tools, specs, safety |
| [superpowers/plans/2026-10-20-mcp-schema-dashboards.md](superpowers/plans/2026-10-20-mcp-schema-dashboards.md) | Implementation tasks |

## Repo entry

Quick start and stack: [../README.md](../README.md)
