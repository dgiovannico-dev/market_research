# ADR-007: Transparent sync — discovery watchlist + user focus (no silent topic defaults)

**Status:** Accepted (revised 2026-10-20)  
**Date:** 2026-10-20  
**Related:** [ADR-001](./ADR-001-evidence-first-kpis.md), [ADR-003](./ADR-003-authorized-connectors-only.md), [manuals/RESEARCH.md](../manuals/RESEARCH.md)

## Context

Collectors accept optional `query: str | None`. When `None`, many search-mode collectors fall back to Settings/env defaults (`*_DEFAULT_QUERY=java`, etc.). The daily scheduler often passes `query=None`, so the corpus is silently skewed.

A first draft of this ADR made **user Research Intents** the only topic-scoped sync path. That removes env lies but **breaks the product purpose**: freelancers need a market radar (rising/cooling tech, geo demand) they did not already know to type—otherwise Executive/Trends and the LLM become an echo chamber.

`SearchQuery` already exists (`search_queries`, FKs on `jobs` / `collection_runs`).

## Decision

1. **Product job:** FMI is a **Demand Compass** — guide freelancers on strong demand, rising/cooling trends, and where demand is stronger, with LLM as an **evidence coach** (never inventing market size).

2. **Dual corpus (both first-class):**
   - **Discovery** (`SearchQuery.kind = discovery`): transparent market-scan probes, seeded from versioned data (e.g. `data/research/discovery_watchlist.json`), visible and disableable in UI. Not hidden in env.
   - **Focus** (`SearchQuery.kind = focus`): user-typed research intents for personal bets.
   - **Dump/feed** collectors run once per tick without a topic string (background board corpus).

3. **Daily crawlers are the normative refresh path.** At least once per day, scheduled authorized collectors run: dump/feed → discovery → focus. Production: cron → `scheduler_tick.sh` → `POST /scheduler/run`. Idempotent per UTC day unless `force`.

4. **Provenance is many-to-many:** `job_intent_matches(job_id, query_id)`. Single `jobs.query_id` is insufficient (dedup updates and multi-intent hits). Lenses query matches, not the legacy FK alone.

5. **Fan-out is budgeted, not cartesian.** Each intent crawls a rotating subset of search collectors under global call ceilings. Full `intents × all search sources` is rejected as default (rate-limit / cost failure).

6. **No silent env topic defaults.** Optional `OPS_SMOKE_QUERY` is ops-only. Discovery topics live in `data/research/discovery_watchlist.json`.

7. **Analytics lenses:** `market` / `focus` / `compare` as in SPEC. UI/LLM read DB only; Sources “Run” is ops/manual exception.

8. **Interactive path (secondary):** DB-first explore; optional one-shot crawl; LLM watch suggestions require accept.

9. **LLM briefs** wrap existing analytics where possible (`technology_trends` for rising/cooling); evidence-only.

## Consequences

### Positive

- Market radar works on day one without env hardcoding.
- Focus deep-dives do not redefine “the market.”
- Provenance via `query_id` + `kind` enables honest LLM coaching.
- Confirmation bias of “query-only” plan is avoided.

### Negative / costs

- Discovery watchlist needs curation; budgeted fan-out means **not every source every day** for every intent (coverage via rotation).
- Users may disable too many discovery probes → thin market lens (UI must warn).
- Extra table `job_intent_matches` and migration from persona-only seeds.

### Neutral

- Evidence-first KPI rules unchanged (ADR-001).
- Product persona framing is not the sync control plane (intents + lenses are).

## Alternatives considered

| Alternative | Why rejected |
|-------------|--------------|
| Keep env defaults as global focus | Opaque; biases corpus and LLM |
| User intents only (first ADR draft) | Confirmation bias; weak discovery |
| Dump/feed only | Weak skill-level coverage on search APIs |
| Full cartesian intent × all search collectors | Rate limits / budget blow-up |
| Lens filter on single `jobs.query_id` | Breaks under dedup + multi-intent |
| Auto-enable LLM-suggested watches | User loses control; surprise API spend |
| One global Settings free-text | No multi-intent, no discovery vs focus split |

## Compliance checklist (implementation)

- [x] `SearchQuery.kind` ∈ {`discovery`, `focus`}
- [x] `job_intent_matches` table; lenses use it
- [x] Discovery seed from data file; visible in UI as Market scan
- [x] Daily crawler cron; dump → discovery → focus with **budgeted** fan-out + idempotency
- [x] Dashboards do not crawl on page view
- [x] No collector Settings topic fallback on product path
- [x] Analytics/API/MCP support `lens` + optional `query_ids`
- [x] LLM watch suggestions require explicit accept
- [x] `.env.example` deprecates topic defaults; documents sync budgets
