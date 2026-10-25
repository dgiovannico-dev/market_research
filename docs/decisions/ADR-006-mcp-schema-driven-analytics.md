# ADR-006: MCP over DB metadata for LLM dashboards & reports

## Status

Accepted (implemented: stdio MCP + validators; in-app UI Later)

## Date

2026-10-20

## Context

Users want to ask natural-language questions and get dashboards/reports. Free-form LLM-to-SQL against production Postgres is unsafe and often invents metrics. FMI already has evidence-first analytics APIs and a known schema. MCP is the standard way for Cursor/agents to call tools with structured results.

## Decision

1. Ship an **`mcp-analytics` module**: an MCP server that exposes **schema metadata**, a **semantic metric catalog**, and **read-only** query/API grounding tools.
2. The LLM produces **`DashboardSpec` / `ReportSpec` JSON**, validated in-repo; it does **not** push raw SQL into the UI.
3. Prefer **existing analytics endpoints** over custom SQL; SQL is a fallback on allowlisted tables with LIMIT/timeout and a read-only role.
4. Keep **RAG** (`rag-knowledge`) for unstructured job text Q&A; MCP owns **structured** analytics composition. They may compose later but stay separate modules.
5. v1 targets **Cursor MCP + pytest**; in-app chat UI is Next/Later using the same contracts.

## Alternatives considered

### LLM writes Next.js pages directly

- Pros: flexible UI
- Cons: unreviewable, breaks design system, hard to test
- Rejected for v1; specs map to known widgets

### Only OpenAPI to the LLM (no MCP)

- Pros: one surface
- Cons: weaker agent UX in Cursor; OpenAPI alone doesn’t give live schema introspection
- Rejected as sole approach; OpenAPI remains listed via `list_analytics_endpoints`

### Full SQL agent without allowlist

- Pros: power
- Cons: injection, writes, PII, fabricated joins
- Rejected

## Consequences

- New dependency: MCP Python SDK (pinned in requirements when implemented).
- Ops must document read-only DB URL for MCP and Cursor config without secrets in git.
- Spec validators become the contract between LLM creativity and product honesty ([ADR-001](ADR-001-evidence-first-kpis.md)).
- Operator wiring: [ops/RUNBOOKS.md](../ops/RUNBOOKS.md) § MCP.
