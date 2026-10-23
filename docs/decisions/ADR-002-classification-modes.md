# ADR-002: Classification modes (rules / hybrid / llm)

## Status

Accepted

## Date

2026-10-20

## Context

The persona works with Ollama/vLLM and needs offline-capable demos. Classification must work without an LLM, and optionally use one when available.

## Decision

Support `CLASSIFICATION_MODE=rules|hybrid|llm` and `LLM_PROVIDER=none|ollama|vllm`. Default hybrid with provider `none` behaves as deterministic rules. LLM outputs are schema-validated; rates are never invented without evidence text.

## Alternatives considered

### LLM-only

- Pros: richer extraction
- Cons: latency, cost, offline failure
- Rejected as sole mode

### Rules-only forever

- Pros: simple
- Cons: blocks persona’s LLM evaluation story
- Rejected; rules remain the baseline path

## Consequences

- Provider abstraction lives in `backend/app/llm/`.
- Evaluation stub measures rules self-consistency until gold labels exist.
- Ops must document that LLM is optional for production MVP.
