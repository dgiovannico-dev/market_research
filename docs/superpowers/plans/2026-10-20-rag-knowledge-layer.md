# RAG Knowledge Layer Implementation Plan

> **For agentic workers:** Do not start until prioritized in [ROADMAP.md](../../ROADMAP.md) Later → Next. Checkbox tasks for when activated.

**Goal:** Add an optional Retrieval-Augmented Generation layer over stored job descriptions (and optional uploaded docs) so the Senior AI persona can ask evidence-cited questions about observed demand.

**Architecture:** Ingest chunks from `jobs.description_original` (+ optional docs) → embeddings → vector store (pgvector or external) → retrieve → LLM answer with citations to job ids/URLs. Keep market KPIs separate; RAG must not invent market size.

**Tech Stack:** Python, existing LLM providers (Ollama/vLLM), PostgreSQL (+ pgvector candidate), FastAPI

**Spec:** Product persona in [PRODUCT.md](../../PRODUCT.md); module id `rag-knowledge` in [CAPABILITY_MAP.md](../../CAPABILITY_MAP.md). Write `docs/specs/SPEC-rag-knowledge.md` before coding.

## Global Constraints

- Citations required; refuse when retrieval empty.
- Authorized data only (jobs already in DB / user-uploaded docs).
- File size ≤ 500 lines; separate ingest/retrieve/generate modules.
- Guardrails: no prompt injection into SQL; tool calls scoped.

## Review Focus

- Hallucinated rates or market totals.
- PII leakage from job descriptions into logs.
- Cost/latency of embedding full corpus.
- Separation from trends-only UI (RAG is guided/assistant surface).

---

### Task 0: Spec gate

- [ ] Author `docs/specs/SPEC-rag-knowledge.md` with acceptance
- [ ] ADR for vector store choice
- [ ] Human review before Task 1

### Task 1: Chunk + embed pipeline

- [ ] Chunking strategy for job text
- [ ] Embedding provider abstraction
- [ ] Persist vectors + job_id references
- [ ] Tests with fixture jobs

### Task 2: Retrieve API

- [ ] `POST /api/v1/rag/query` → chunks + scores
- [ ] Hybrid lexical+vector optional

### Task 3: Answer with citations

- [ ] LLM generate grounded on chunks only
- [ ] UI panel (guided mode); hidden or optional in trends-only
- [ ] Eval stub: citation presence rate

## Checkpoint

- [ ] Empty corpus returns safe refusal
- [ ] Answers include job links/ids
- [ ] pytest + build green
