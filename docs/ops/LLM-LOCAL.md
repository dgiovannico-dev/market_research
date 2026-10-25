# Local LLM on this machine (Apple Silicon)

FMI talks to an **OpenAI-compatible** chat API (`/v1/chat/completions`) via:

| `LLM_PROVIDER` | Typical base URL | Notes |
|----------------|------------------|--------|
| `ollama` | `http://localhost:11434` | Best fit for Mac |
| `vllm` | `http://localhost:8001/v1` | Expects a Linux + NVIDIA CUDA host |

Admin UI can override env at runtime ([ADR-010](../decisions/ADR-010-admin-llm-runtime-config.md)): **Ops → Sources → LLM runtime**.

---

## Your hardware (detected)

| Item | Value |
|------|--------|
| Chip | **Apple M1 Pro** (arm64) |
| Unified memory | **16 GB** |
| GPU | Apple (Metal 3), not NVIDIA |

### Can you run vLLM here?

**No — not in a useful way.** [vLLM](https://docs.vllm.ai/) targets **Linux + CUDA (NVIDIA)**. There is no stable Metal/MPS backend for vLLM on macOS. On this Mac you should **not** install vLLM for FMI.

Use one of:

1. **Ollama** (recommended on this Mac) — native Metal, already wired as `LLM_PROVIDER=ollama`
2. **Remote vLLM** on a Linux box / cloud GPU, and point FMI at that URL as `vllm`
3. **LM Studio / llama.cpp server** exposing OpenAI API, then set `LLM_PROVIDER=vllm` only as a *label* for “OpenAI-compatible” (same HTTP shape)

---

## Recommended path: Ollama + 7B-class model (16 GB)

### 1. Install Ollama

```bash
brew install ollama
# or: https://ollama.com/download
ollama serve   # leave running (or enable the macOS app)
```

### 2. Pull a model that fits 16 GB unified memory

Leave headroom for macOS + Chrome + Docker (~4–6 GB). Prefer **Q4/Q5** quantizations around **3B–8B**:

```bash
# Strong default for briefs / classification (Italian+English OK)
ollama pull qwen2.5:7b

# Lighter / faster alternative
ollama pull llama3.2:3b

# If you want more quality and can close other apps
ollama pull mistral:7b
```

Avoid 70B / 32B / large “instruct” full-precision models on 16 GB — they will swap or fail.

Smoke test:

```bash
ollama run qwen2.5:7b "Reply with one short sentence."
```

### 3. Point FMI at Ollama

In repo-root `.env` (from `.env.example`):

```bash
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_MODEL=qwen2.5:7b
CLASSIFICATION_MODE=hybrid
```

If the API runs **on the host** (not Docker), use `http://localhost:11434` instead of `host.docker.internal`.

Restart the API container so settings reload:

```bash
docker compose up -d api
# or: COMPOSE_STACK_FORCE=1 ./scripts/compose_stack_relaunch.sh
```

Optional: open **Ops → Sources**, set provider **Ollama**, model `qwen2.5:7b`, save (needs ops token / admin).

### 4. Verify

```bash
curl -sf http://127.0.0.1:11434/api/tags | head
curl -sf http://127.0.0.1:8000/readyz
# In UI: Research → Assistant, or Study Advisor refine when LLM is up
```

---

## If you still want “vLLM” semantics (OpenAI `/v1`)

### A) Remote NVIDIA box

On a Linux machine with an NVIDIA GPU:

```bash
# example — adjust GPU memory / model
pip install vllm
vllm serve Qwen/Qwen2.5-7B-Instruct --port 8001
```

On this Mac’s `.env`:

```bash
LLM_PROVIDER=vllm
VLLM_BASE_URL=http://<gpu-host>:8001/v1
VLLM_MODEL=Qwen/Qwen2.5-7B-Instruct
VLLM_API_KEY=
```

### B) Local OpenAI-compatible server (not vLLM, same API shape)

Examples: **LM Studio** (enable Local Server) or `llama-server` from llama.cpp. Then:

```bash
LLM_PROVIDER=vllm
VLLM_BASE_URL=http://host.docker.internal:1234/v1
VLLM_MODEL=<name-shown-in-lm-studio>
```

FMI only needs chat completions; it does not require the vLLM engine itself.

---

## Model pick cheat-sheet (M1 Pro 16 GB)

| Goal | Model | Why |
|------|--------|-----|
| Default FMI briefs / hybrid classify | `qwen2.5:7b` | Good multilingual, fits Metal |
| Fast / low RAM | `llama3.2:3b` | Snappy on 16 GB |
| Stronger English reasoning | `mistral:7b` | Close other heavy apps |

Do **not** run Docker Postgres + browser + a 13B+ model at full context without watching Activity Monitor (Memory pressure).

---

## Related

- Env template: [../../.env.example](../../.env.example) (`LLM_*`, `OLLAMA_*`, `VLLM_*`)
- Admin UI: [../manuals/ADMIN.md](../manuals/ADMIN.md)
- Decision: [ADR-010](../decisions/ADR-010-admin-llm-runtime-config.md)
- Local stack: [LOCAL.md](LOCAL.md)
