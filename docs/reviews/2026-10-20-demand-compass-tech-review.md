# Tech review: Demand Compass proposal

**Date:** 2026-10-20  
**Verdict:** Direction is right; several **must-fix** gaps before implementation. Corrections applied to SPEC / ADR-007 / plan.

## Against codebase (facts)

| Area | Today | Proposal risk |
|------|--------|----------------|
| Scheduler | `run_enabled_collectors(query=None)` once; no intents | Must rewrite, not tweak |
| `SearchQuery` | `name`, countries/role_families/contract_types; **no** `kind` | Map fields; add `kind`/`origin`/`deleted_at` |
| `jobs.query_id` | Set **only on insert**; updates ignore new intent | Single FK **cannot** power lenses |
| Classify | Inline in `upsert_raw_job` | No separate `classify_pending()` needed |
| Trends | `technology_trends` half-period growth already exists | LLM `rising_cooling` should wrap this, not reinvent |
| Collectors | ~40; many fall back to env defaults | Mode metadata + strip defaults |
| Seed intents | Persona Java/AI focus starters only | Split discovery file vs focus starters |

## Must-fix (blocker)

### 1. Many-to-many intent matches (not single `jobs.query_id`)

A job can be seen by dump (null), then discovery, then focus. Dedup updates **do not** change `query_id` today. Even if they did, overwriting would drop the job from the other lens.

**Correction:** introduce `job_intent_matches(job_id, query_id, first_matched_at, last_matched_at)` (unique pair). Keep `jobs.query_id` optional as “first acquiring intent” only, or deprecate for lens filters. **Lenses query the match table.**

### 2. Fan-out must not be full cartesian by default

`~10 discovery × ~25 search collectors ≈ 250` calls/day (+ focus) will hit rate limits and budgets immediately.

**Correction:** default strategy = **budgeted pairing**, not full product:

1. Dump/feed: once each (required).
2. For each intent: crawl a **priority subset** of search collectors (round-robin / `source_priority` / geo affinity from intent filters), capped by `SYNC_MAX_COLLECTOR_CALLS_PER_INTENT` and global tick cap.
3. Optional Later: per-source “supports query” capability flags.

### 3. Market lens definition must use matches + dump

`market` = canonical jobs that are either unlabeled (dump-only) **or** matched to any `kind=discovery` intent.  
`focus` = matched to selected focus intents.  
A job can appear in **both** (compare uses that).

### 4. Query syntax is best-effort

Watchlist strings with `OR` will break or no-op on many APIs. Collectors must send a **simplified query** (first clause / keywords) when the API has no boolean support; document per connector.

## Should-fix (important)

| Issue | Correction |
|-------|------------|
| Field naming `label` vs `name` | SPEC API may expose `label`; persist as `name` or rename once |
| Filters JSON vs columns | Keep columns; map `filters` DTO → columns; extra keys in JSON column `filters_extra` if needed |
| `classify_pending()` in algorithm | Replace with “classify during ingest (current)” |
| Sources UI “Run all” | Allowed **ops/manual** exception; not the product freshness path |
| Daily idempotency | Record `crawler_ticks` or skip duplicate same UTC day unless `force=true` |
| Multi-user | MVP single-tenant (no `user_id` on intents); note Later |
| Partial tick resume | Persist progress counters; next day continues; no complex checkpoint MVP |
| Discovery seed vs existing persona seed | On migrate: mark existing seed rows `kind=focus, origin=seed_focus`; insert discovery from JSON |
| ATS / RemoteOK / Remotive | `collection_mode=dump` (or feed); do not require query |
| Credentialed search sources | Only in fan-out when keys present + connector enabled |

## Nice-to-have (Later)

- Intent × source eligibility matrix in catalog
- Crawl parallelism with per-host rate limits
- Soft-filter dump corpus by discovery keywords client-side
- Multi-user owned focus intents

## What stays correct

- Dual discovery + focus (fixes confirmation bias)
- No silent env topic defaults
- Daily crawlers as normative freshness
- DB-first UI; LLM evidence-only briefs with accept-to-watch
- Evidence-first KPI semantics (ADR-001)

## Doc updates from this review

- [SPEC-research-intents.md](../specs/SPEC-research-intents.md) §3.2, §3.3, §6, §14
- [ADR-007](../decisions/ADR-007-query-first-sync.md)
- [plan](../superpowers/plans/2026-10-20-query-first-daily-sync.md)
