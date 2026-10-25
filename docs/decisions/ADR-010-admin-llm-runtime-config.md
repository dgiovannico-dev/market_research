# ADR-010: Admin LLM runtime config overrides env

## Status

Accepted

## Date

2026-10-25

## Context

LLM provider was env-only (`LLM_PROVIDER`, Ollama/vLLM URLs). Product needs admin GUI to switch Ollama / OpenAI-compatible / Gemini and version prompts without redeploy. Secrets must stay admin-only (ADR-009).

## Decision

1. **Singleton DB config** `llm_runtime_config` is the runtime source of truth when a row exists and `provider != none` (or explicitly set).
2. **Env bootstrap:** if no DB row (or decrypt fails), fall back to Settings env (`llm_provider`, ollama_*, vllm_*).
3. **API keys** stored Fernet-encrypted with `CREDENTIALS_MASTER_KEY` (same as connector credentials). Responses expose `api_key_set` only.
4. **Prompt registry** in DB; active version resolved per purpose slug at call time.
5. **Admin-only** mutation via `require_admin` (+ OPS break-glass when OIDC off).

## Consequences

- Deployments must keep master key stable or re-enter API keys after rotation.
- Smoke/CI can leave provider `none` and skip LLM paths.
- Classify / weekly / study advisor share one gateway factory invalidated on settings PUT.
