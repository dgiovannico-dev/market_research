# ADR-001: Evidence-first KPIs (observed ≠ market size)

## Status

Accepted

## Date

2026-10-20

## Context

Freelance market tools often imply “market size” from incomplete scrapes. FMI’s persona needs trustworthy signals for positioning decisions. Overstating coverage destroys trust.

## Decision

All KPIs and dashboards report **observed records in this database**. Every KPI includes definition, sample size, evidence kind, and limits (surfaced in guided mode). Missing rates stay NULL.

## Alternatives considered

### Invent or extrapolate market totals

- Pros: flashy numbers
- Cons: misleading; not defensible
- Rejected

### Hide sample size

- Pros: simpler UI
- Cons: user cannot judge confidence
- Rejected for guided mode; trends-only may shorten copy but still must not invent totals

## Consequences

- Product copy and API payloads carry methodology metadata.
- Growth may be `insufficient_data`.
- Marketing language must stay aligned with this ADR.

## Implementation note (Demand Compass DSS, 2026-10)

- **`Job.evidence_tier`** (`standard` | `thin`) tags capped or snapshot-only sources (e.g. ViewJobs, Job Bank CA). Thin rows are stored and visible in inventory; they are not treated as full posting evidence.
- Analytics endpoints default **`min_evidence=standard`**: skills co-occurrence, rates, technology trends, and LLM brief sample sizes (`lens_sample_size`) exclude thin jobs unless the client opts down.
- **Quality by_source** still lists all observed jobs per connector, including **`pct_thin`**, so operators can see thin share without inflating skill/rate KPIs.
- Dashboard **summary** and **countries** may include **`coverage_notes`** when limits apply (aligned with guided-mode honesty).
