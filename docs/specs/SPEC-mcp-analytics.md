# Spec: mcp-analytics (schema MCP → dashboards & reports)

## Objective

Expose FMI PostgreSQL **metadata** (and safe, read-only data access) through an **MCP server** so an LLM can interpret a natural-language user prompt and produce:

1. A validated **dashboard specification** (widgets, filters, period) over observed data.
2. A validated **report specification** (sections, KPIs, narrative grounded in query results).

Evidence-first: the LLM must not invent market size, rates, or coverage. Outputs cite sample size, period, and definition ([ADR-001](../decisions/ADR-001-evidence-first-kpis.md)).

## Persona & use cases

Primary: Senior AI & Backend freelancer (and operators) asking e.g.:

- “Mostra trend Java + RAG ultimi 90 giorni, remoto EU”
- “Report settimanale: skill gaps vs mio profilo, rates dichiarati mediani”
- “Quali fonti ACTIVE contribuiscono più job questo mese?”

Consumers:

- **Cursor / agent** via MCP tools (dev and analysis).
- **In-app assistant** (Later/Next UI) calling the same tool contract through the API or MCP bridge.

## Architecture (logical)

```
User prompt
    → LLM (Cursor or FMI llm provider)
    → MCP tools: schema / semantics / safe_query / propose_dashboard / propose_report / render_demand_brief
    → Validator (JSON Schema + allowlist + evidence rules)
    → Renderer: dashboard prefs/widgets OR report markdown/JSON
```

The MCP server is **schema-first**: it always offers structural metadata before ad-hoc SQL. Prefer composing existing analytics APIs over free-form SQL when possible.

## In scope

### MCP server (`mcp-analytics`)

Transport: stdio (Cursor) + optional HTTP/SSE for in-app (Later).

**Tools (minimum):**

| Tool | Purpose |
|------|---------|
| `get_db_metadata` | Tables, columns, types, nullability, FKs, indexes; optional SQLAlchemy comments |
| `get_semantic_catalog` | Named metrics, evidence_kind, definitions, allowed filters (skills, country, period, source status, **query_ids / research intents**) |
| `list_analytics_endpoints` | Existing `/api/v1/*` market endpoints the LLM should prefer |
| `run_readonly_query` | Parameterized SELECT against allowlisted views/tables; hard LIMIT; timeout |
| `get_observed_counts` | Cheap aggregates (jobs by period, sources ACTIVE count, optional intent scope) for grounding |
| `propose_dashboard` | Input: user prompt + optional `lens` / `query_ids` / brief constraints → `DashboardSpec` JSON |
| `propose_report` | Input: user prompt + optional `lens` / `query_ids` / `brief_type` → `ReportSpec` + grounded draft |
| `render_demand_brief` | Required `brief_type` + optional `lens` (default `market`), `query_ids`, `period_days` → grounded brief JSON from `render_brief` (disclose `n=` / `sample_size`). Types: `rising_cooling`, `where_demand`, `adjacent`, `focus_vs_market`, `suggest_watches` ([SPEC-research-intents](SPEC-research-intents.md) §4 J5 / §10). `suggest_watches` returns candidates only — no INSERT |
| `validate_spec` | Validate DashboardSpec/ReportSpec against schema and policy |

**Resources (optional MCP resources):**

- `fmi://schema/summary` — cached metadata snapshot
- `fmi://semantics/metrics` — KPI catalog
- `fmi://evidence/rules` — short ADR-001/003 rules for the model

### Spec schemas (product contracts)

`DashboardSpec` (v1):

- `title`, `period_days`, `view_mode` (`guided` | `trends_only`)
- `filters`: technologies[], countries[], source_keys[], contract_types[], **query_ids[]** (optional Research Intent scope)
- `widgets[]`: `{ id, type, metric_key, params }` where `type` ∈ chart/table/kpi/quality
- `disclaimer_mode`: inherit from `view_mode`
- `grounding`: `{ sample_size?, queries_used[], intent_labels?[] }` filled after validation/execution; disclose scoped intents when applied

`ReportSpec` (v1):

- `title`, `period_days`, `sections[]` (`summary` | `rates` | `skills` | `sources` | `gaps` | `custom`)
- `include_profile_gaps`: bool
- `grounding`: query ids / endpoint calls + sample sizes
- `narrative_policy`: `observed_only` (required)

### Safety & policy

- DB role **read-only**; no INSERT/UPDATE/DELETE/DDL via MCP.
- Allowlist tables/views (jobs, job_skills, job_rates, sources, market_metrics_daily, technologies, collection_runs, …). Deny `audit_logs` secrets, credential fields, raw env.
- Max rows, statement timeout, no multi-statement.
- Rates: never coerce NULL → 0; refuse “invent median if empty”.
- Prompt injection: treat user text as data; tools ignore instructions that request write or scrape.

### Persistence (app, not MCP process memory)

- Optional: save approved specs as `saved_filters` / new `generated_artifacts` table (prompt hash, spec JSON, created_at).
- Weekly report path may consume `ReportSpec` alongside existing `reports/weekly.py`.

## Out of scope (v1)

- Writing connectors or mutating catalog status via MCP.
- Arbitrary scrape / external web tools.
- Claiming RAG over free text (that is `rag-knowledge`); MCP may *complement* RAG later.
- Auto-deploying generated Next.js pages without human approve (v1 returns spec + preview data).
- Multi-tenant OAuth (uses existing API_KEY / local trust model).

## Acceptance criteria

- [x] MCP starts with `DATABASE_URL` (read-only preferred) and exposes `get_db_metadata` with real FMI tables.
- [x] `get_semantic_catalog` lists metrics aligned with SPEC-analytics (definition + sample semantics).
- [x] `run_readonly_query` rejects non-SELECT / non-allowlisted / over-limit.
- [x] Given a fixture prompt, `propose_dashboard` returns JSON that `validate_spec` accepts and that maps to existing widget/metric keys.
- [x] Given a fixture prompt, `propose_report` returns sections grounded with `get_observed_counts` or analytics endpoints — no fabricated rates.
- [x] Docs: Cursor MCP install snippet in README / SPEC-ops; `.env.example` vars.
- [x] Pytest for allowlist + validators; live metadata/query tests against Postgres.
- [x] `render_demand_brief` registered; pytest covers every `BRIEF_TYPE` structure (`brief_type`, `sample_size`, `narrative`, `limits`); `suggest_watches` does not INSERT `SearchQuery`.
- [x] `list_analytics_endpoints` includes `POST /assistant/brief` and `POST /research/watches/accept`.
- [x] ADR-006 accepted; ROADMAP Next/Later placement clear.
- [ ] In-app assistant UI apply specs (Later / Task 17).

## Commands (target)

```bash
# MCP stdio (Cursor)
cd backend && python -m app.mcp.server

# Metadata smoke
# (tool) get_db_metadata → includes jobs, sources, job_rates
```

## Key paths (planned)

- `backend/app/mcp/` — server, tools, allowlist, validators
- `backend/app/mcp/semantics.py` — metric catalog
- `backend/app/mcp/specs.py` — DashboardSpec / ReportSpec Pydantic models
- `backend/tests/test_mcp_*.py`
- Cursor config: `.cursor/mcp.json` or user MCP settings (documented, not secrets)
- UI Later: `frontend/app/assistant/` or Explorer “Generate from prompt”

## Related

- [SPEC-analytics.md](SPEC-analytics.md)
- [SPEC-dashboard.md](SPEC-dashboard.md)
- [SPEC-ops.md](SPEC-ops.md)
- Plan: [../superpowers/plans/2026-10-20-mcp-schema-dashboards.md](../superpowers/plans/2026-10-20-mcp-schema-dashboards.md)
- ADR: [../decisions/ADR-006-mcp-schema-driven-analytics.md](../decisions/ADR-006-mcp-schema-driven-analytics.md)
- RAG (complementary): [../superpowers/plans/2026-10-20-rag-knowledge-layer.md](../superpowers/plans/2026-10-20-rag-knowledge-layer.md)
