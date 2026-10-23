# Idea: Freelance Demand Compass

**Status:** adopted — shipped (supersedes narrow “query-only corpus”); ops walkthrough + automatable smoke shipped ([ops/demand-compass-walkthrough.md](../ops/demand-compass-walkthrough.md); `smoke_compass.sh` / `COMPASS_ACCEPT_WATCH=1`)

**Date:** 2026-10-20  
**Related:** [SPEC-research-intents.md](../specs/SPEC-research-intents.md), [ADR-007](../decisions/ADR-007-query-first-sync.md), [plan](../superpowers/plans/2026-10-20-query-first-daily-sync.md)  
**Previous draft:** [query-first-research-corpus.md](./query-first-research-corpus.md) (merged; kept for history)

## Problem statement

How might FMI help a senior IT freelancer decide **which technologies to deepen, which are cooling, and where demand is stronger**—using an honest observed corpus and an LLM that **interprets evidence**, never invents market size—without silently hardcoding “java” in collectors **and** without trapping the user in confirmation bias (only seeing what they already searched)?

## What was wrong in the first plan

Making **only** user-typed intents drive search-mode sync fixes env hardcoding, but breaks the product job:

| If we only sync what the user types… | Failure mode |
|--------------------------------------|--------------|
| User watches “Java Spring” | Never sees rising “Rust” / “AI agents” in Executive/Trends |
| Empty focus intents | Thin search-API corpus; dump alone may lack structured skill coverage |
| LLM scoped only to focus | Echo chamber coaching |

**Correction:** dual corpus + dual analytics lenses. User intents are for **focus**, not the sole market radar.

## Recommended direction — Demand Compass

FMI is a **Demand Compass** for freelancers:

```
Discover (market)  →  Focus (my bets)  →  Decide (skills / geo / rates)
         ↑                    │
         └──── LLM proposes new watches (user accepts) ────┘
```

### Layer A — Discovery corpus (market radar)

- **Dump/feed** collectors sync once per daily tick (broad boards/RSS).
- **Discovery Watchlist:** explicit, versioned, **visible** system probes (`SearchQuery.kind = discovery`), seeded from `data/research/discovery_watchlist.json` (not silent env vars).
- Covers a **balanced IT/freelance scan** (languages, cloud, AI/RAG, contract/remote cues)—editable/disableable by the user; labeled “Market scan”, not “your research”.
- Powers default **Executive / Trends / Skills / Countries** (lens = `market`).

### Layer B — Focus corpus (personal bets)

- User **Research Intents** (`kind = focus`): free text + filters the user typed.
- Daily budgeted crawlers + optional Refresh; jobs linked via **`job_intent_matches`** (not a single overwritable `query_id`).
- Powers **Profile gaps, Focus dashboard strip, compare mode**.

### Layer C — Decide with LLM (evidence coach)

LLM/MCP **only** over DB aggregates. Productized briefs (not free chat as MVP):

1. **Rising / cooling** — skills or tech with period-over-period Δn (and rates when present), with sample sizes.
2. **Where demand is** — countries / remote mix for a skill or for market.
3. **Adjacent opportunity** — co-occurrence near profile skills the user does **not** list yet.
4. **Focus vs market** — is my watched stack growing slower/faster than the discovery corpus?
5. **Watch suggestions** — propose new discovery/focus intents from observed co-occurrence; **user must accept** before they join the watchlist.

Always: evidence_kind, `n=`, period, limits; refuse when sample too thin ([ADR-001](../decisions/ADR-001-evidence-first-kpis.md)).

### Analytics lenses (UI + API)

| Lens | Default use |
|------|-------------|
| `market` | Discovery + dump/feed jobs (exclude focus-only if needed, or include all unlabeled) |
| `focus` | Jobs linked to user’s focus `query_ids` (+ optional profile skill filter) |
| `compare` | Side-by-side market vs focus for the same metric |

No silent env topic defaults. Discovery probes are first-class rows the user can inspect.

## Why this is effective

- **Discovery** answers “what’s hot / cooling / where?” without requiring the user to already know the keyword.
- **Focus** answers “how is *my* bet doing?” without polluting the market narrative with a private niche query.
- **LLM** accelerates interpretation and suggests next watches—still grounded.
- **Removes** env `*_DEFAULT_QUERY` lies while keeping a **transparent** market scan.

## Key assumptions

1. Dump/feed alone is insufficient for skill-level trends on search-heavy sources → discovery watchlist is required.
2. Users will tolerate a visible “Market scan” list if they can disable probes; opacity (env java) they will not.
3. Compare lens is the killer UX for positioning decisions.
4. KPI semantics stay observed-in-DB; lenses only change the filter set.

## MVP scope

- Intent `kind`: `discovery` | `focus` (+ soft-delete, enable, schedule_hint).
- Seed discovery watchlist from data file; seed focus starters from persona (editable).
- **Daily crawlers** (cron in production): dump once → discovery fan-out → focus fan-out (budgets); DB is the read path for UI/LLM.
- Remove product path env topic defaults.
- UI: Market scan list + My focus intents; Explore DB-first; lens toggle on Executive/Trends.
- Assistant/MCP: five brief types above + `lens` / `query_ids` parameters.

## Not doing

- Inventing total market demand or filling missing rates.
- Auto-adding LLM-suggested watches without user accept.
- Per-keystroke live scrape.
- Replacing structured MCP briefs with ungrounded chat.
- Putting discovery topics back into `.env` as the control plane.

## Success looks like

- Fresh install: Executive shows rising/cooling skills from **discovery + dump**, with honest `n=`.
- User adds focus “Enterprise RAG CH/DE” → Focus lens and compare show personal vs market.
- LLM brief: “Adjacent: LangGraph co-occurs with your RAG skill (n=…) — add watch?” → user accepts → next sync deepens that signal.
- No collector env var silently forces a profession the user never chose.
