# ADR-008: Hexagonal + DDD — incremental adoption

## Status

Accepted — Waves 0–8 landed (2026-10-23); Wave 9 (Job aggregate) deferred until write-path pain

## Date

2026-10-23

## Context

The backend is a FastAPI modular monolith (~24k LOC) with clear feature packages but no ports, no composition root, and SQLAlchemy `Session` leaked into API, analytics, ingestion, and MCP. A multi-agent audit recommended Hexagonal Architecture (ports & adapters) combined with DDD bounded contexts — without a greenfield rewrite.

## Decision

Adopt Hexagonal + DDD **incrementally by seam**:

1. **Ports-first, entities later.** Introduce driven ports (`JobWriteRepository`, `CollectorGateway`, …) and application use cases (`RunSource`, `IngestBatch`, …) wrapping current SQLAlchemy/ORM. Do **not** dual-map domain entities for every table while analytics `GROUP BY` ORM columns.
2. **Preserve ubiquitous language** from ADR-001…007 (evidence, lenses, connectors, discovery/focus). Refactor must not rename product terms for “purer DDD English.”
3. **CQRS-light only.** Keep `analytics/` as SQL read adapters; no projected read DB or per-KPI repositories until a second store is required.
4. **Single crawl path.** HTTP `POST /sources/{id}/run` and the daily scheduler share one `RunSource` use case.
5. **Thin domain package.** Extract pure invariants (classification rules, evidence tier, closed-status corpus set) first; introduce a write-side `Job` aggregate only when status FSM / canonical merge demand it.
6. **One deployable package.** Folder layout is documented in [architecture/OVERVIEW.md](../architecture/OVERVIEW.md); no microservices split.

## Alternatives considered

### Big-bang domain rewrite

- Pros: clean layer names immediately
- Cons: high risk to crawl/KPI behavior; dual mapping cost; rejected

### Ports only on new code

- Pros: less churn
- Cons: duplicate crawl paths and Session leakage remain; rejected as insufficient

## Consequences

- Migration waves 0–8 delivered: shared kernel, `RunSource`, `AppContainer`, write/acquire/catalog/credentials ports, research intents, briefs/assistant application slice, market_queries + `ExternalStatsGateway`. Wave 9 stays gated.
- HTTP must not import `app.mcp`; MCP and assistant share `application/briefs` + `application/assistant`.
- Tests and smoke stay green; ≤500 LOC/file rule unchanged.
- ADR-001/003/006/007 constraints remain hard gates on any further extraction.
