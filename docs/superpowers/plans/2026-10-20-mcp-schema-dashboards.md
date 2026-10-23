# MCP Schema → Dashboards & Reports Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an MCP server that introspects FMI DB metadata and a semantic metric catalog so an LLM can turn a user prompt into validated `DashboardSpec` / `ReportSpec` artifacts grounded in observed data.

**Architecture:** Python MCP server (stdio) shares the app’s SQLAlchemy models and analytics semantics. Tools expose metadata → safe reads → propose/validate specs. Rendering reuses existing dashboard widgets and report builders; the LLM never invents rates or market totals.

**Tech Stack:** Python 3.12, MCP Python SDK, FastAPI/SQLAlchemy (existing), Pydantic v2, PostgreSQL read-only role, pytest; Cursor MCP config for local agents.

**Spec:** [docs/specs/SPEC-mcp-analytics.md](../../specs/SPEC-mcp-analytics.md) · [ADR-006](../../decisions/ADR-006-mcp-schema-driven-analytics.md)

## Global Constraints

- Evidence-first: observed DB only; NULL rates stay NULL ([ADR-001](../../decisions/ADR-001-evidence-first-kpis.md)).
- Read-only DB access for MCP; no scrape / write connectors ([ADR-003](../../decisions/ADR-003-authorized-connectors-only.md)).
- Source files ≤ 500 lines; split `backend/app/mcp/` by responsibility.
- No secrets in git; document `DATABASE_URL_READONLY` / MCP env in `.env.example`.
- Prefer analytics API composition over free SQL.

## Review Focus

- Prompt injection asking for DDL/writes → tools must refuse (Task 3).
- Empty rate sample → report must say “undeclared”, not invent median (Task 5).
- Metadata drift after migrations → regenerate from live models/information_schema (Task 2).
- Spec with unknown `metric_key` → `validate_spec` fails closed (Task 4).
- Cursor MCP misconfig leaking write credentials → docs mandate read-only URL (Task 7).

## File map

| Path | Responsibility |
|------|----------------|
| `backend/app/mcp/__init__.py` | Package |
| `backend/app/mcp/server.py` | MCP entry (stdio), tool registration |
| `backend/app/mcp/metadata.py` | Schema introspection from SQLAlchemy + optional information_schema |
| `backend/app/mcp/semantics.py` | Metric / filter catalog aligned with analytics |
| `backend/app/mcp/allowlist.py` | Tables/views + query policy |
| `backend/app/mcp/query.py` | `run_readonly_query` + counts helpers |
| `backend/app/mcp/specs.py` | Pydantic `DashboardSpec`, `ReportSpec` |
| `backend/app/mcp/propose.py` | Deterministic proposal helpers (LLM may call; server can also template) |
| `backend/app/mcp/validate.py` | Policy validation |
| `backend/tests/test_mcp_allowlist.py` | SQL policy |
| `backend/tests/test_mcp_specs.py` | Spec validation |
| `backend/tests/test_mcp_metadata.py` | Metadata includes core tables |
| `docs/specs/SPEC-mcp-analytics.md` | Already authored |
| `.env.example` | MCP env vars |
| `docs/ops` / README snippet | Cursor MCP wiring |

---

### Task 1: Spec models + semantic catalog

**Files:**
- Create: `backend/app/mcp/specs.py`
- Create: `backend/app/mcp/semantics.py`
- Test: `backend/tests/test_mcp_specs.py`

**Interfaces:**
- Produces: `DashboardSpec`, `ReportSpec`, `MetricDef`, `get_semantic_catalog() -> list[MetricDef]`

- [x] **Step 1–4:** Specs, semantic catalog, tests green (`test_mcp_specs.py`)
- [ ] **Step 5: Commit** (when requested)

---

### Task 2: DB metadata introspection

**Files:**
- Create: `backend/app/mcp/metadata.py`
- Test: `backend/tests/test_mcp_metadata.py`

**Interfaces:**
- Consumes: SQLAlchemy `Base.metadata` / engine
- Produces: `get_db_metadata() -> dict` with `tables[].name|columns[]|foreign_keys[]`

- [x] **Step 1: Write failing test** asserting metadata includes `jobs`, `sources`, `job_rates`, `job_skills`.

- [x] **Step 2: Run** pytest → FAIL

- [x] **Step 3: Implement** introspection from mapped metadata (prefer models over ad-hoc SQL); optional live enrich.

- [x] **Step 4: Run** pytest (uses app DB fixture / Postgres service) → PASS

- [ ] **Step 5: Commit** `feat(mcp): expose FMI schema metadata`

---

### Task 3: Allowlist + read-only query

**Files:**
- Create: `backend/app/mcp/allowlist.py`
- Create: `backend/app/mcp/query.py`
- Test: `backend/tests/test_mcp_allowlist.py`

**Interfaces:**
- Produces: `run_readonly_query(sql: str, params: dict, limit: int = 100) -> QueryResult`
- Produces: `get_observed_counts(period_days: int) -> dict`

- [x] **Step 1: Write failing tests**: reject `DELETE`, reject non-allowlisted table, accept simple `SELECT count(*) FROM jobs`, enforce max limit.

- [x] **Step 2: Run** pytest → FAIL

- [x] **Step 3: Implement** parser/guard (sqlparse or statement prefix checks + allowlist) + timeout + LIMIT clamp; `get_observed_counts` via SQLAlchemy.

- [x] **Step 4: Run** pytest → PASS

- [ ] **Step 5: Commit** `feat(mcp): read-only allowlisted queries`

---

### Task 4: validate_spec + propose helpers

**Files:**
- Create: `backend/app/mcp/validate.py`
- Create: `backend/app/mcp/propose.py`
- Modify: `backend/tests/test_mcp_specs.py`

**Interfaces:**
- Produces: `validate_spec(spec: DashboardSpec | ReportSpec) -> ValidationResult`
- Produces: `propose_dashboard_from_intent(intent: IntentHints) -> DashboardSpec` (deterministic from parsed hints; LLM fills hints via tools)

- [x] **Step 1: Write failing tests**: unknown metric fails; guided vs trends_only widget sets; report with empty rates section sets `insufficient_data` flag not fake numbers.

- [x] **Step 2: Implement** validators + template proposer from filters (tech/country/period).

- [x] **Step 3: pytest → PASS; commit deferred
- [ ] Commit `feat(mcp): validate and propose dashboard/report specs`

---

### Task 5: MCP server wiring (stdio tools)

**Files:**
- Create: `backend/app/mcp/server.py`
- Create: `backend/app/mcp/__main__.py` (so `python -m app.mcp` works)
- Modify: `backend/requirements.txt` (MCP SDK pin)
- Test: `backend/tests/test_mcp_server_tools.py` (call tool handlers in-process, not full stdio)

**Interfaces:**
- Tools: `get_db_metadata`, `get_semantic_catalog`, `list_analytics_endpoints`, `run_readonly_query`, `get_observed_counts`, `propose_dashboard`, `propose_report`, `validate_spec`

- [x] **Step 1: Add dependency** + failing test that each tool handler returns JSON-serializable payload.

- [x] **Step 2: Implement** FastMCP/official SDK server registering handlers from Tasks 1–4.

- [x] **Step 3: Manual** `python -m app.mcp` starts without error (stdio idle).

- [ ] **Step 4: Commit** `feat(mcp): stdio MCP server with analytics tools`

---

### Task 6: Grounded report path (bridge weekly report)

**Files:**
- Modify: `backend/app/reports/weekly.py` (thin adapter) **or** Create: `backend/app/mcp/render_report.py`
- Test: `backend/tests/test_mcp_report_grounding.py`

**Interfaces:**
- Produces: `materialize_report(spec: ReportSpec) -> dict` with `sections[].data` from analytics helpers + `narrative` only after data attached

- [x] **Step 1: Failing test** — materialize with zero jobs → narrative contains insufficient/empty language, no invented EUR rates.

- [x] **Step 2: Implement** materialize using existing analytics modules.

- [x] **Step 3: pytest → PASS; commit deferred
- [ ] Commit `feat(mcp): ground ReportSpec in analytics results`

---

### Task 7: Ops docs + Cursor MCP config example

**Files:**
- Modify: `.env.example`
- Modify: `docs/specs/SPEC-ops.md`
- Modify: `docs/PRODUCTION.md`
- Modify: `README.md` (short MCP section)
- Create: `docs/mcp/CURSOR.md` (install snippet; no secrets)

- [x] **Step 1: Document** `DATABASE_URL_READONLY`, `python -m app.mcp`, example Cursor `mcp.json` pointing at venv python.

- [x] **Step 2: Recommend** Postgres role `GRANT SELECT` only.

- [ ] **Step 3: Commit** `docs(mcp): Cursor wiring and read-only DB guidance`

---

### Task 8 (Next/Later): In-app prompt → preview

**Files (when prioritized):**
- `frontend/app/assistant/page.tsx` or Explorer panel
- API: `POST /api/v1/assistant/propose` wrapping same validators (no need for browser to speak MCP)

- [ ] Spec UI acceptance: user enters prompt → sees DashboardSpec preview → “Apply” writes dashboard prefs / opens Trends with filters
- [ ] Does not ship until Tasks 1–7 green

---

## Checkpoint

- [x] pytest mcp suite green in CI
- [ ] Manual Cursor session: ask “trend remote Java 90d” → agent uses metadata + propose_dashboard → valid spec
- [x] No write queries possible via tool tests
- [x] Docs linked from [docs/README.md](../../README.md)

## Dependency on other work

- Works with current analytics APIs; better UX after dashboard customization prefs (Tasks 1–4 in `tasks/todo.md`) so “Apply DashboardSpec” can set `view_mode` / widgets.
- Complementary to RAG plan; do not block on embeddings.
