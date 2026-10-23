# Spec: classify

## Objective

Classify ingested jobs into contract type, remote type, seniority, country, skills, and rates using rules, optional LLM, or hybrid mode—always with evidence metadata.

## In scope

- `CLASSIFICATION_MODE=rules|hybrid|llm`
- `LLM_PROVIDER=none|ollama|vllm`
- Taxonomy + alias index for technologies.
- Rate parsing; missing rates stay NULL.
- Batch LLM classify endpoint and rules self-consistency evaluation stub.

## Out of scope

- Large-scale gold F1 / inter-annotator agreement as a market KPI.
- Inventing rates via LLM without text evidence.

## Acceptance criteria

- [x] Rules path works with `LLM_PROVIDER=none`.
- [x] LLM outputs validated (Pydantic); invalid responses do not corrupt stored rates.
- [x] Stored fields carry `*_evidence_kind` / extraction method where applicable.
- [x] `POST /api/v1/llm/evaluation/run` returns field agreement metrics (self-consistency).
- [x] `GET|POST /api/v1/llm/evaluation/gold` scores rules against `data/eval/gold_labels.json` (Quality UI).
- [x] `GET /api/v1/llm/status` reports mode and provider health.

## Key paths

- `backend/app/classification/`
- `backend/app/normalization/rates.py`
- `backend/app/llm/`
- ADR: [../decisions/ADR-002-classification-modes.md](../decisions/ADR-002-classification-modes.md)
