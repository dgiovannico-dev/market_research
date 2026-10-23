# Implementation Plan: FMI completeness (post-docs + global sources)

## Overview

Documentation under `docs/` is the source of truth—including the **global sources** program and the planned **MCP schema → dashboards/reports** module. This plan sequences **code** slices: dashboard customization, production hardening, MCP analytics, credentialed sources when keys exist, then optional gold eval and RAG.

**2026-10-22:** IT/CH/LU coverage research complete — see [IT_CH_LU_COVERAGE.md](../docs/sources/IT_CH_LU_COVERAGE.md) and implementation slices in [2026-10-22-it-ch-lu-sources.md](../docs/superpowers/plans/2026-10-22-it-ch-lu-sources.md) (Task 29). Do not ship EURES/`jv-search` or expand JobCloud public APIs without partner/legal OK.

**2026-10-22:** Complete chart dashboard (Task 30) — draft SPEC [SPEC-dashboard-charts.md](../docs/specs/SPEC-dashboard-charts.md) + plan [2026-10-22-complete-chart-dashboard.md](../docs/superpowers/plans/2026-10-22-complete-chart-dashboard.md). Awaiting SPEC approval before coding.

## Architecture decisions

- Presentation modes are UI preferences ([ADR-004](../docs/decisions/ADR-004-dashboard-modes.md)); analytics APIs stay evidence-first ([ADR-001](../docs/decisions/ADR-001-evidence-first-kpis.md)).
- Preferences v1: versioned localStorage; profile sync later.
- Multi-replica: external cron + `ENABLE_SCHEDULER=false` ([hardening plan](../docs/superpowers/plans/2026-10-20-production-hardening.md)).
- Connectors: authorized/public only ([ADR-003](../docs/decisions/ADR-003-authorized-connectors-only.md)); catalog is system of record ([ADR-005](../docs/decisions/ADR-005-global-source-catalog.md)).
- LLM dashboards/reports via MCP + validated specs, not free SQL ([ADR-006](../docs/decisions/ADR-006-mcp-schema-driven-analytics.md)).
- RAG / stats-ingest / procurement are Later until explicitly prioritized.

## Task list

Tracked in [todo.md](todo.md):

- Tasks 1–4: dashboard customization
- Tasks 5–7: production hardening (parallel-safe with 1–4)
- Tasks 15–16: MCP metadata server + Cursor wiring ([mcp plan](../docs/superpowers/plans/2026-10-20-mcp-schema-dashboards.md))
- Tasks 10+: credentialed connectors + catalog maintenance (when keys available)
- Task 8–9: gold eval / RAG (Later)

Detailed steps:

- Dashboard: [../docs/superpowers/plans/2026-10-20-dashboard-customization.md](../docs/superpowers/plans/2026-10-20-dashboard-customization.md)
- Sources expansion: [../docs/superpowers/plans/2026-10-20-global-sources.md](../docs/superpowers/plans/2026-10-20-global-sources.md)
- MCP: [../docs/superpowers/plans/2026-10-20-mcp-schema-dashboards.md](../docs/superpowers/plans/2026-10-20-mcp-schema-dashboards.md)

## Risks

| Risk | Mitigation |
|------|------------|
| Trends-only still shows coaching via shared components | Acceptance checklist in SPEC-dashboard; review Executive/Profile embeds |
| Dual scheduler ticks | PRODUCTION + cron script; default scheduler off |
| False ACTIVE source claims | Live tests + validation report; never invent credentials |
| LLM invents rates via MCP | validate_spec + materialize_report refuse empty medians |
| MCP with write DB URL | Docs + prefer DATABASE_URL_READONLY |
| Scope creep into RAG/Java/K8s/stats | Keep Later; do not claim shipped |

## Open questions

None blocking dashboard customization. MCP Tasks 15–16 can start after analytics stable (parallel with hardening). Credentialed connectors wait on real API keys. RAG vector store choice deferred to ADR at Task 0 of RAG plan.

## References

- [docs/README.md](../docs/README.md)
- [docs/PRODUCT.md](../docs/PRODUCT.md)
- [docs/CAPABILITY_MAP.md](../docs/CAPABILITY_MAP.md)
- [docs/ROADMAP.md](../docs/ROADMAP.md)
- [docs/sources/VALIDATION_REPORT.md](../docs/sources/VALIDATION_REPORT.md)
