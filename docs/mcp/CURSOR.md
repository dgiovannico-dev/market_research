# Cursor MCP wiring (FMI analytics)

Spec: [../specs/SPEC-mcp-analytics.md](../specs/SPEC-mcp-analytics.md) · Plan: [../superpowers/plans/2026-10-20-mcp-schema-dashboards.md](../superpowers/plans/2026-10-20-mcp-schema-dashboards.md)

## Install

```bash
cd backend
source .venv/bin/activate
pip install -r requirements.txt
# ensure Postgres is up and migrations applied
```

Prefer a **SELECT-only** role in `DATABASE_URL_READONLY` (falls back to `DATABASE_URL`).

## Operator checklist (Cursor loads `.cursor/mcp.json`)

Do this on the machine where you want Agent MCP tools:

1. **Copy example** — from repo root: `cp .cursor/mcp.json.example .cursor/mcp.json` (live file is gitignored; commit only the example).
2. **Absolute paths** — edit `.cursor/mcp.json`: replace both `/ABSOLUTE/PATH/TO/market_research/...` placeholders with this machine’s absolute paths to `backend/.venv/bin/python` and `backend/`; set `env.DATABASE_URL` (and optional `DATABASE_URL_READONLY`, or `""` to fall back). Do **not** commit secrets.
3. **Restart Cursor** (or reload MCP servers) after saving.
4. **Settings → MCP** — confirm server **`fmi-analytics`** is green / tools listed (expect **11** tools).
5. **Smoke** (backend venv): `python -c "from app.mcp.server import build_mcp; build_mcp()"`.

If smoke passes but Settings still lacks the server: re-check absolute paths, that `.venv` exists, and that Postgres accepts `DATABASE_URL`.

## Create project `.cursor/mcp.json`

The live config is **gitignored** (see `.gitignore`). Commit only the example.

```bash
# from repo root
cp .cursor/mcp.json.example .cursor/mcp.json
```

Then edit `.cursor/mcp.json`:

1. Replace both `/ABSOLUTE/PATH/TO/market_research/...` placeholders with this machine’s absolute paths to `backend/.venv/bin/python` and `backend/`.
2. Set `env.DATABASE_URL` to the same local Postgres URL the API uses (dev defaults from `.env.example` are fine for localhost).
3. Optionally set `env.DATABASE_URL_READONLY` to a SELECT-only URL; leave `""` to fall back to `DATABASE_URL`.
4. Do **not** commit `.cursor/mcp.json` or production passwords.
5. **Restart Cursor** (or reload MCP servers) after saving.

Example shape (paths must be absolute):

```json
{
  "mcpServers": {
    "fmi-analytics": {
      "command": "/absolute/path/to/backend/.venv/bin/python",
      "args": ["-m", "app.mcp"],
      "cwd": "/absolute/path/to/backend",
      "env": {
        "DATABASE_URL": "postgresql+psycopg://fmi:…@localhost:5432/fmi",
        "DATABASE_URL_READONLY": "postgresql+psycopg://fmi_readonly:…@localhost:5432/fmi"
      }
    }
  }
}
```

## Verify (without trusting Cursor UI yet)

Smoke the server module:

```bash
cd backend && python -c "from app.mcp.server import build_mcp; build_mcp(); print('ok')"
```

Optional tool list (expect **11** tools including `get_semantic_catalog`, `propose_dashboard`, `render_demand_brief`):

```bash
cd backend && python - <<'PY'
import asyncio
from app.mcp.server import build_mcp
async def main():
    m = build_mcp()
    tools = await m.list_tools()
    print(len(tools), sorted(t.name for t in tools))
asyncio.run(main())
PY
```

## Confirm Cursor loaded the config

1. Cursor → **Settings → MCP** (or Features → MCP).
2. Server name should be **`fmi-analytics`**.
3. Status green / tools listed after restart.
4. In Agent chat, tools from that server should appear in the MCP tool catalog.

If the file exists and smoke passes but Cursor still shows the server missing: check absolute paths, that `.venv` exists, and that Postgres accepts `DATABASE_URL`.

## Agent usage pattern

1. `get_db_metadata` / `get_semantic_catalog` / `evidence_rules`
2. Interpret the user prompt → `propose_dashboard` or `propose_report`
3. `validate_spec`
4. `get_observed_counts` / prefer HTTP analytics endpoints; `run_readonly_query` only if needed
5. `materialize_report` before writing narrative — never invent rates
