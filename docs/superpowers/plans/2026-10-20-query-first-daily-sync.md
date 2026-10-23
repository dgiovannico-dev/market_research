# Plan: Demand Compass sync (discovery + focus)

> **For agentic workers:** Implement task-by-task. Prefer TDD. Keep files ≤500 lines. No silent env topic defaults. Do not make user intents the only market radar.

**Goal:** Ship a Freelance **Demand Compass** whose corpus is refreshed by **daily crawlers** (scheduled authorized collectors): discovery watchlist + focus intents; lenses (`market` / `focus` / `compare`); LLM evidence briefs; no `*_DEFAULT_QUERY` product path.

**Architecture:** [SPEC-research-intents.md](../../specs/SPEC-research-intents.md) · [ADR-007](../../decisions/ADR-007-query-first-sync.md) · [idea](../../ideas/freelance-demand-compass.md)

**Tech stack:** FastAPI, SQLAlchemy/Alembic, existing scheduler, Next.js, Postgres, pytest.

---

## Corrections from reviews

| Mistake | Fix |
|---------|-----|
| User intents only → confirmation bias | Dual: discovery then focus |
| Executive powered only by focus | Default lens = `market` |
| Seed = persona only | Discovery JSON + focus starters |
| Single `jobs.query_id` for lenses | **`job_intent_matches` M2M** |
| Full cartesian fan-out | Budgeted subset + daily rotation |
| `classify_pending()` step | Classify stays in ingest upsert |
| LLM reinvent trends | `rising_cooling` wraps `technology_trends` |

Review: [../../reviews/2026-10-20-demand-compass-tech-review.md](../../reviews/2026-10-20-demand-compass-tech-review.md)

---

## File map

| Area | Paths |
|------|--------|
| Discovery seed | `data/research/discovery_watchlist.json` (create) |
| Models | `SearchQuery` + `kind`, `origin`, soft-delete |
| Alembic | new revision |
| Settings | `config.py`, `.env.example` (budgets; remove topic defaults) |
| Collectors | `collection_mode`; no topic fallback |
| Scheduler | dump → discovery → focus |
| Analytics | `lens` + `query_ids` on market endpoints |
| API | `research.py` intents + accept watches |
| Assistant/MCP | `brief_type` handlers |
| Frontend | Market scan, My focus, lens toggle, brief chips |
| Tests | `backend/tests/` |

---

### Task 1: Registry `collection_mode`

Annotate every collector `search|dump|feed`. Test: all registered have a mode.

### Task 2: Intent model + `job_intent_matches` + discovery seed

- Add `kind`, `origin`, `schedule_hint`, `deleted_at`, optional `filters_extra`.
- Migration: `job_intent_matches(job_id, query_id, first_matched_at, last_matched_at)` unique pair.
- Migrate existing seed rows → `kind=focus`, `origin=seed_focus`.
- Seed discovery from `data/research/discovery_watchlist.json`.
- Ingest: on crawl with `query_id`, upsert match even when job already exists.

### Task 3: Collector contract + modes

Annotate `collection_mode`. Search-mode blank → `missing_query`. Strip topic defaults. `simplify_query_for(collector, text)` for APIs without boolean OR.

### Task 4: Daily crawler (budgeted)

`run_daily_crawlers` / `scheduler_tick`: dump → discovery → focus with **pick_search_collectors** rotation + global ceiling + UTC-day idempotency. `collection_runs` + matches. Cron in PRODUCTION.md.

### Task 5: Analytics lenses

`lens` + `query_ids` on summary/trends/skills/countries/rates using **match table**. Default `market`. Tests for dual-match and focus-only exclusion.

### Task 6: Research API

CRUD by kind; sync one intent; `POST /research/watches/accept`; `GET /research/jobs` DB-only.

### Task 7: Frontend Demand Compass

- Lens toggle on Executive/Trends.
- Market scan panel + My focus CRUD.
- Explore DB-first + Refresh.
- Warn if discovery enabled count low.
- No “java” default placeholder.

### Task 8: LLM / MCP briefs

Implement brief types: `rising_cooling`, `where_demand`, `adjacent`, `focus_vs_market`, `suggest_watches` (+ accept). Disclose lens/`n=`.

### Task 9: Docs + verification

Align CAPABILITY_MAP/PRODUCT/ROADMAP/todo; pytest; manual compass walkthrough.

**Docs alignment (done 2026-10-20):** PRODUCT / ROADMAP / CAPABILITY_MAP / `tasks/todo.md` Task 27–28 reflect shipped vs remaining. Superseded “query-only” / java-default product framing is historical only ([ideas/query-first-research-corpus.md](../../ideas/query-first-research-corpus.md)).

---

## Done when

- [x] SPEC §11 acceptance criteria true **in code + pytest** (dual-match lenses, budgets, idempotency, no topic defaults, accept-only suggests, Explore DB-first, cron docs).
- [x] Market lens works with zero focus intents after discovery sync (lens via `job_intent_matches` + discovery; tests in `test_analytics_lenses.py`)
- [x] No product path env topic defaults (`test_collection_mode.py`; `.env.example` deprecation block)
- [x] Suggest watches require accept (`suggest_watches` never INSERTs; `POST /research/watches/accept`; UI `WatchCandidates`)
- [x] Docs point to Demand Compass (not query-only)
- [x] Manual compass walkthrough documented + automatable smoke ([ops/demand-compass-walkthrough.md](../../ops/demand-compass-walkthrough.md); `smoke_compass.sh` / `COMPASS_ACCEPT_WATCH=1`)

## Verification notes (Task 9)

| Area | Evidence in repo | Status |
|------|------------------|--------|
| `collection_mode` + no defaults | `backend/tests/test_collection_mode.py` | Done |
| Daily crawlers budget + idempotency | `backend/tests/test_daily_crawlers.py`, `PRODUCTION.md` cron | Done |
| Lenses / dual-match | `backend/tests/test_analytics_lenses.py` | Done |
| Briefs + accept (API + MCP) | `test_briefs.py`, `test_mcp_briefs.py`, `render_demand_brief` | Done |
| UI Market scan / Focus / LensToggle | `frontend/app/[locale]/market-scan`, `focus`, `LensToggle.tsx` | Done |
| Explorer DB-first + Refresh | `explorer/page.tsx` + `ExplorerRefresh.tsx` | Done |
| Assistant brief chips + accept in UI | `/assistant` → `DemandCompassSection` chips + `WatchCandidates` | Done |
| Ops manual walkthrough | [ops/demand-compass-walkthrough.md](../../ops/demand-compass-walkthrough.md); `smoke_compass.sh` | Done |

## Out of scope

- RAG, auto-enable watches, inventing KPIs, per-keystroke scrape
