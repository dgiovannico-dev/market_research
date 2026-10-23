# SPEC-research-intents — Demand Compass: discovery + focus

**Status:** Ready for implementation (revised)  
**Date:** 2026-10-20  
**ADR:** [ADR-007](../decisions/ADR-007-query-first-sync.md)  
**Idea:** [freelance-demand-compass.md](../ideas/freelance-demand-compass.md)  
**Plan:** [2026-10-20-query-first-daily-sync.md](../superpowers/plans/2026-10-20-query-first-daily-sync.md)

## 1. Goal

Make FMI an effective **Demand Compass** for freelancers:

- See **strong demand**, **rising / cooling** signals, and **where** demand concentrates (geo / remote).
- Deep-dive **personal focus** stacks without poisoning the market narrative.
- Use the **LLM as evidence coach** over Postgres—not as a market oracle.
- Collect with **transparent** discovery probes + user focus intents—**never** silent env profession defaults.

## 2. Non-goals

- Inventing total market size or filling missing rates ([ADR-001](../decisions/ADR-001-evidence-first-kpis.md)).
- Auto-subscribing LLM watch suggestions without user accept.
- Live scrape on every keystroke.
- RAG over raw HTML (Later).
- Putting discovery topics back into `.env` as the control plane.

## 3. Domain model

### 3.1 Research Intent (`SearchQuery`)

| Field (logical) | Persist / notes |
|-----------------|-----------------|
| `id` | PK |
| `kind` | `discovery` \| `focus` (**new**) |
| `name` | Human label (API may alias as `label`) |
| `query_text` | Free text for search-mode collectors |
| `countries`, `role_families`, `contract_types` | Existing structured filters |
| `filters_extra` JSON | Optional (**new**, nullable) for remote/seniority/etc. not in columns |
| `enabled` | Scheduled fan-out when true |
| `schedule_hint` | `daily` \| `manual_only` (**new**) |
| `origin` | `seed_discovery` \| `seed_focus` \| `user` \| `llm_accepted` (**new**) |
| `deleted_at` | Soft-delete (**new**) |
| timestamps | Existing |

**Rules**

- Discovery intents seeded from `data/research/discovery_watchlist.json`.
- Existing persona seed rows migrate to `kind=focus`, `origin=seed_focus`.
- Empty `query_text` → invalid for search-mode.
- Query syntax is **best-effort** per collector (boolean `OR` may be simplified).
- Warn in UI if enabled discovery count &lt; soft threshold (e.g. 3).

### 3.2 Provenance (must-fix vs single FK)

**Problem:** `jobs.query_id` is a single FK and today is set only on insert. Dedup updates do not attach new intents; overwriting would break the other lens.

| Record | Role |
|--------|------|
| `collection_runs.query_id` | Intent that triggered that run (null for dump-only) |
| `jobs.query_id` | Optional **first acquiring** intent only (legacy/debug); **not** used for lenses |
| **`job_intent_matches`** | **Normative:** `(job_id, query_id)` unique; `first_matched_at`, `last_matched_at`. Upsert on every crawl hit |

Dump/feed crawls create/update jobs **without** a match row (unlabeled background). Discovery/focus crawls upsert a match for that intent.

### 3.3 Analytics lenses

| Lens | Job set (canonical jobs) |
|------|---------------------------|
| `market` | Jobs with **no** focus-only restriction: unlabeled (no matches) **OR** matched to ≥1 `kind=discovery` intent. Default Executive/Trends/Skills/Countries |
| `focus` | Jobs matched to selected `kind=focus` `query_ids` (default: all enabled focus) |
| `compare` | Both sets + overlap counts; paired series |

A job may sit in **both** market and focus via multiple matches. API: `lens=` + optional `query_ids[]`.

### 3.4 Source modes

| Mode | With query/intent | Without query |
|------|-------------------|---------------|
| **search** | Call API with `query_text` | Skip `missing_query` — never invent topic |
| **dump** / **feed** | Optional soft-filter | Sync authorized feed once per tick |

Registry: `collection_mode: search | dump | feed`.

## 4. User journeys (product)

### J0 — Open the compass (default)

1. User opens Executive (lens=`market`).
2. Sees rising/cooling skills, geo breakdown, sample sizes from discovery + dump.
3. Guided mode shows methodology; trends-only strips coaching chrome.

### J1 — Market scan management

1. User opens **Market scan** (discovery intents).
2. Can enable/disable probes, edit labels/text, see last sync counts.
3. Cannot accidentally confuse them with “My focus.”

### J2 — Define focus

1. User types free text (+ filters) → saves as **My focus** intent.
2. Confirmation: included in next daily sync; available for Focus / Compare lenses.

### J3 — Explore (DB-first)

1. Search Postgres by text / intent / lens.
2. Secondary: **Refresh from sources** for that query/intent.
3. Empty state: sync or refresh—not “invented” empty charts.

### J4 — Daily crawlers (normative data refresh)

**Product rule:** freshness of the Demand Compass corpus comes from **scheduled daily crawlers**, not from ad-hoc UI clicks. Manual “Refresh from sources” is a supplement for one intent, not the primary pipeline.

Each calendar day (ops cron preferred in production; single-replica in-process scheduler only if cron is unavailable):

1. Trigger `run_daily_crawlers()` (alias of daily sync / `POST /api/v1/scheduler/run`).
2. Run **authorized collectors** only ([ADR-003](../decisions/ADR-003-authorized-connectors-only.md)) — API/RSS/board fetchers, never ToS-bypass scraping.
3. Order:

```
dump/feed crawlers once (all enabled dump/feed)
→ discovery intents × budgeted search-collector subset
→ focus intents × budgeted search-collector subset
→ classify happens inside ingest (current upsert path)
→ alert evaluation
```

4. Persist `collection_runs` (+ `query_id` when intent-driven); upsert **`job_intent_matches`**; ops summary: discovery/focus ran, skips, budget hits, errors.
5. Prefer **idempotent daily tick** (skip or no-op if already succeeded for UTC day unless `force=true`).
6. Dashboards/LLM read the **DB**; they do not crawl on page view. Sources UI “Run …” remains an **ops/manual** exception.

### J5 — LLM evidence coach

User (or MCP) requests a **brief type**:

| Brief | Output (grounded) |
|-------|-------------------|
| `rising_cooling` | Wrap existing `technology_trends` (half-period Δ) + rates when present; lens default `market` |
| `where_demand` | Countries / remote mix for skill or market |
| `adjacent` | Co-occurrence near profile skills not yet in profile |
| `focus_vs_market` | Compare lens narrative + numbers |
| `suggest_watches` | Proposed intents; **persist only after accept** |

Refuse or thin-sample disclose when `n` below threshold.

## 5. API surface (target)

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/research/intents?kind=` | List discovery and/or focus |
| `POST` | `/research/intents` | Create (`kind` required; discovery create may be admin-only or allowed with label) |
| `PATCH` | `/research/intents/{id}` | Update / enable / disable |
| `DELETE` | `/research/intents/{id}` | Soft-delete |
| `POST` | `/research/intents/{id}/sync` | Collect for one intent |
| `POST` | `/research/watches/accept` | Accept LLM-suggested watch → create enabled intent |
| `GET` | `/research/jobs` | DB search: `q`, `lens`, `query_id`, filters |
| `GET` | `/market/*` (existing) | Add `lens` + `query_ids` query params |
| `POST` | `/assistant/propose` / MCP briefs | Accept `brief_type`, `lens`, `query_ids` |
| `POST` | `/ops/collect/run` | Explicit `query_id` or `query_text` only |

## 6. Daily crawler algorithm (normative)

**Cadence:** once per day minimum in production (cron e.g. `0 3 * * *`). More frequent ticks allowed under the same budgets.

**Fan-out policy (must-fix):** do **not** default to full cartesian `intents × all search collectors`. That can exceed ~200–400 calls/day with current ACTIVE set.

```
on daily_crawler_tick:   # cron → scheduler_tick.sh → POST /scheduler/run
  if already succeeded today and not force: return skipped_idempotent

  dump = enabled collectors mode in (dump, feed)   # remotive, remoteok, ATS boards, RSS, …
  search_pool = enabled collectors mode == search and credentials_ok
  discovery = enabled SearchQuery kind=discovery, schedule != manual_only
  focus = enabled SearchQuery kind=focus, schedule != manual_only
  calls = 0

  for c in dump:
    crawl(c, query=None)                         # no intent match rows
    calls += 1

  for intent in discovery[:SYNC_MAX_DISCOVERY_PER_TICK]:
    subset = pick_search_collectors(intent, search_pool,  # round-robin / geo affinity
                                    lim=SYNC_MAX_COLLECTOR_CALLS_PER_INTENT,
                                    global_left=TOTAL-calls)
    for c in subset:
      q = simplify_query_for(c, intent.query_text)
      crawl(c, query=q, query_id=intent.id) → upsert jobs + job_intent_matches
      calls += 1

  for intent in focus[:SYNC_MAX_FOCUS_PER_TICK]:
    … same budgeted subset pattern …

  evaluate_alerts()   # classify already done in ingest upsert
```

`pick_search_collectors`: stable rotation across days so each search source gets coverage over a week; prefer sources whose geo matches intent `countries` when known.

Budgets (Settings):

- `SYNC_MAX_DISCOVERY_PER_TICK`
- `SYNC_MAX_FOCUS_PER_TICK`
- `SYNC_MAX_COLLECTOR_CALLS_PER_INTENT` (small, e.g. 3–8)
- `SYNC_MAX_TOTAL_COLLECTOR_CALLS_PER_TICK` (hard ceiling, e.g. 80–120)

**Ops contract:** production MUST schedule daily crawler (cron + `ENABLE_SCHEDULER=false` on API replicas). See [SPEC-ops.md](SPEC-ops.md), [PRODUCTION.md](../PRODUCTION.md).  
Tech review: [../reviews/2026-10-20-demand-compass-tech-review.md](../reviews/2026-10-20-demand-compass-tech-review.md).

## 7. Collector contract

1. **Forbidden:** Settings `*_DEFAULT_QUERY` / `*_DEFAULT_WHAT` / `*_DEFAULT_TAG` as product topic when `query` is None.
2. **Allowed:** page limits, hosts, timeouts, credentials.
3. Search-mode blank query → skip `missing_query`.
4. Dump/feed may ignore query (default) or soft-filter when present.
5. On crawl with `query_id`, ingest **upserts `job_intent_matches`** even when the job row already existed.

## 8. Configuration / env

### Remove from product path

All topic-like collector defaults (see `.env.example` deprecation block).

### Keep / add

| Var | Purpose |
|-----|---------|
| `SYNC_MAX_DISCOVERY_PER_TICK` | Discovery budget |
| `SYNC_MAX_FOCUS_PER_TICK` | Focus budget |
| `SYNC_MAX_COLLECTOR_CALLS_PER_INTENT` | Per-intent cap |
| `SYNC_MAX_TOTAL_COLLECTOR_CALLS_PER_TICK` | Global cap |
| `OPS_SMOKE_QUERY` | Explicit ops smoke only |

Discovery topic list lives in **`data/research/discovery_watchlist.json`**, not env.

## 9. Frontend

- **Executive / Trends:** default lens `market`; toggle Focus / Compare.
- **Market scan** panel: discovery intents CRUD-lite (enable/disable/edit).
- **My focus:** full intent CRUD + Sync now.
- **Explore:** DB-first; Refresh secondary; no default “java” placeholder.
- **Assistant:** brief-type chips (rising/cooling, where, adjacent, compare, suggest watches) + Apply / Accept watch.
- Warn when discovery enabled count is below a soft threshold (e.g. < 3).

## 10. LLM / MCP

- Tools accept `brief_type`, `lens`, `query_ids`, `period_days`.
- Reports disclose lens + intent labels + `n=`.
- `suggest_watches` returns candidates only; `POST /research/watches/accept` persists.
- Never claim “market demand” beyond observed DB counts.

## 11. Acceptance criteria

1. Fresh seed: market lens shows signals after daily crawler **without** focus intents and **without** env topic defaults.
2. Production documents **daily cron** for crawlers.
3. Same physical job matched by discovery then focus has **two** `job_intent_matches` rows; appears in both lenses.
4. Budgeted fan-out never exceeds `SYNC_MAX_TOTAL_COLLECTOR_CALLS_PER_TICK`.
5. Disabling all discovery + focus → search skips; dump may run; UI warns thin market.
6. Compare lens returns paired metrics; market is not redefined solely by a niche focus intent.
7. LLM `suggest_watches` persists only after accept.
8. Explore/dashboards read DB on view (Sources manual run = ops exception).
9. Idempotent: second tick same UTC day skips unless `force`.
10. `.env.example` points topics to discovery watchlist + focus UI.

## 12. Test plan (minimum)

| Layer | Cases |
|-------|--------|
| Unit | Search skip without query; dump without query |
| Unit | Scheduler order dump → discovery → focus within budgets |
| Unit | Lens via `job_intent_matches`; job in both lenses when dual-matched |
| Unit | Fan-out respects global call ceiling (not full cartesian) |
| API | CRUD by kind; accept watch; market endpoints honor `lens` |
| Integration | Brief rising_cooling wraps `technology_trends`; thin `n` refused |
| Regression | No Settings topic default on product collect path |

## 13. Rollout

1. Model `kind` + discovery seed file + collector skip behavior.
2. Scheduler dual fan-out + lens on analytics APIs.
3. UI Market scan + My focus + lens toggle.
4. Assistant/MCP brief types + accept watches.
5. Remove Settings topic fields.

## 14. Resolved defaults

| Question | Decision |
|----------|----------|
| Dump once per tick? | Yes |
| Discovery from env? | **No** — data file + DB rows |
| Provenance model | **`job_intent_matches` M2M** (not single `jobs.query_id` for lenses) |
| Fan-out | **Budgeted subset** + rotation, not full cartesian |
| User can edit discovery text? | Yes |
| User can create discovery kind? | MVP: edit/disable seed; create mainly focus |
| Market includes dump jobs? | Yes (unlabeled) |
| Market includes focus-matched jobs? | Only if also discovery-matched or unlabeled; focus-only stays in focus lens |
| Soft-delete? | Yes |
| Multi-user intents? | Later (MVP single-tenant) |
| Query boolean syntax? | Best-effort simplify per collector |
