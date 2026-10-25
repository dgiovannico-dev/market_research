# ADR-005: Global source catalog as system of record

## Status

Accepted

## Date

2026-10-20

## Context

The product must track ~193 candidate sources across aggregators, marketplaces, agencies, ATS, statistics, surveys, FX/taxonomies, procurement, and discovery aids—without claiming integration for unverified entries. Agents and operators need a single expandable registry.

## Decision

1. **Canonical registry:** [`data/sources/catalog.json`](../../data/sources/catalog.json), generated/maintained via `backend/scripts/generate_source_catalog.py`, synced to Postgres on seed.
2. **Categories A–I** label source type; duplicates use `duplicate_of` instead of deleting important names.
3. **Verification status** on each entry drives UI honesty; runnable connectors are a strict subset.
4. **Evidence for ACTIVE** lives in catalog verification fields, DB `source_verifications`, and collection-run inserts—not invented pass results. Catalog file: `data/sources/catalog.json`.
5. **Later modules** (stats-ingest, procurement) stay separate entities; catalog rows may exist before ingest paths exist.

## Alternatives considered

### Wiki-only list without DB sync

- Pros: simpler
- Cons: UI/API cannot filter; seed drift
- Rejected for production Sources dashboard

### Only store ACTIVE sources

- Pros: small table
- Cons: loses gap visibility and credential backlog
- Rejected

## Consequences

- Product/specs/roadmap must link the catalog and never equate catalog size with coverage.
- New connectors update catalog status only after live tests; see [ops/RUNBOOKS.md](../ops/RUNBOOKS.md) § connectors.
