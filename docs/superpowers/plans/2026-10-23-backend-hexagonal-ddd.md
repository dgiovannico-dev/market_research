# Backend refactor — Hexagonal Architecture + DDD

> **For agentic workers:** REQUIRED SUB-SKILL: Use incremental-implementation / executing-plans task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. Do **not** big-bang rewrite `backend/app`. Preserve ADR-001…007 language and behavior.

**Date:** 2026-10-23  
**Method:** [Hexagonal (Ports & Adapters)](https://alistair.cockburn.us/hexagonal-architecture/) + strategic/tactical [DDD](https://www.domainlanguage.com/ddd/blue-book/) (Clean Architecture dependency rule)  
**Companion audits:** multi-agent pass over `collectors`, `ingestion`/`classification`, `storage`, `analytics`/`research`, `api`/`mcp`/`scheduler`, ADRs  
**Stack:** FastAPI monolith · SQLAlchemy · ~24k LOC · ~64 collectors · anemic ORM + transaction scripts  

---

## 1. Verdict

Adopt Hexagonal + DDD **incrementally by seam**, not by inventing a full `domain/` tree for every table.

| Reality today | Implication |
|---|---|
| ~70–80% product logic already outside routes | Drivers are mostly thin; gravity is **Session-everywhere** + **duplicate crawl paths** |
| Models are anemic (`Job` ≈ 40+ columns) | **Do not** dual-map entities first — ports over ORM, then one Job write aggregate if invariants demand it |
| Classification + normalization are already Session-free | First real **domain** candidates |
| Analytics is SQL/CQRS-light over ORM | Keep as **read adapters**; optional thin query facades — not domain entities |
| Collectors = ACL swarm + `RawJob` DTO | Treat as **driven adapters**; extract registry/credentials ports, not a Job aggregate |
| ADRs already encode ubiquitous language | Refactor must **preserve** evidence tiers, lenses, connectors, discovery/focus — not rename for purity |

**Grade:** moderate–high leverage if we merge crawl paths + introduce composition root + write ports; **high cost / low value** if we greenfield-entity every table while KPIs still `GROUP BY` ORM columns.

---

## 2. As-is architecture (compressed)

```
Driver adapters          Application-ish (Session leaked)         Driven
─────────────────        ─────────────────────────────────        ──────────────────
FastAPI api/v1/*  ──┐
MCP handlers      ──┼──► ingestion / research / analytics / llm ──► storage.models (ORM)
Scheduler tick    ──┤         │                                    collectors/* (httpx)
Ops + scripts     ──┘         ├── classification (pure ✓)
                              └── collectors.registry (eager import)
```

**Critical smells**

1. **Duplicate write path:** `api/v1/router.run_source` vs `scheduler/crawl_run.crawl_one`
2. **No composition root:** `deps.py` = auth only; MCP/scheduler each open `SessionLocal`
3. **HTTP → MCP imports** (`assistant` → `mcp.propose`) — peer adapter coupling
4. **Collector → ingestion reverse edge** (`arbetsformedlingen` → `adzuna_country`)
5. **Write → read leak:** `ingestion.country_backfill` → `analytics.job_query.CLOSED_JOB_STATUSES`
6. **Three truths for connectors:** catalog JSON · `COLLECTORS` · DB `Source.verification_status`
7. **Lens policy duplicated:** `research/jobs_search.apply_research_job_scope` reimplements market/focus scoping instead of `analytics.lenses`

---

## 3. Ubiquitous language (freeze — do not “improve away”)

From ADRs 001–007 + SPEC — these names stay in code and APIs:

| Term | Meaning |
|---|---|
| **Observed ≠ market size** | KPIs = DB sample; never invent totals |
| **Evidence kind / tier** | `standard` \| `thin`; default `min_evidence=standard` |
| **Connector** vs **catalog entry** | Runnable path ⊂ catalog SoR (`catalog.json`) |
| **Research intent (`SearchQuery`)** | `discovery` \| `focus` |
| **`job_intent_matches`** | Normative provenance (not sole `jobs.query_id`) |
| **Lens** | `market` \| `focus` \| `compare` |
| **Collection mode** | `search` \| `dump` \| `feed` |
| **Demand Compass** | Product job; LLM = evidence coach |
| **DashboardSpec / ReportSpec** | Validated MCP/assistant outputs (no free SQL to UI) |

Hard constraints that survive any folder move: ADR-003 (authorized only), ADR-007 (dual corpus, budgeted fan-out, no silent env topics), ADR-006 (schema specs).

---

## 4. Bounded contexts (strategic)

```
[Catalog] ──eligibility──► [Acquisition] ──RawJob──► [Ingestion]
     ▲                          ▲                        │
     │ SoR sync                 │ budgets/creds          ▼
[Ops/Platform] ─────────────────┘              [Classification]
     │                                                  │
     │ daily dump→discovery→focus                       ▼
[Research Intents] ──matches/lenses──► [Market Analytics] ──OHS──► Dashboard / MCP / Briefs
```

| Context | Core language | Today’s folders (approx) | Subdomain |
|---|---|---|---|
| **Catalog** | verification status, ACTIVE, categories A–I | `sources/`, seed catalog sync | Core |
| **Acquisition** | connector, collection_mode, RawJob, dump_complete | `collectors/`, credentials slice | Core |
| **Ingestion** | Job identity, dedup, soft-expire, snapshots, intent match | `ingestion/` | Core |
| **Classification** | rules/hybrid/llm, taxonomy aliases, ParsedRate | `classification/`, `normalization/` | Core |
| **Research Intents** | discovery/focus, sync budget, rematch | `research/` | Core |
| **Market Analytics** | lens, KPI, coverage_notes, evidence_gate | `analytics/` | Core |
| **Demand Compass App** | briefs, specs, compare payload | `llm/briefs*`, MCP propose | Supporting |
| **Ops/Platform** | tick, credentials crypto, rate limit, health | `scheduler/`, `secrets/`, `ops/`, `core/` | Supporting |
| **Profile** | prefs, skills, outcomes | `models_user`, profile API | Supporting / thin |
| **FX / Stats / Taxonomy clients** | conversion, Eurostat/ADEM, ESCO | `fx/`, `stats/`, `taxonomy/` | Generic — adapters only |

**Context relations (short):** Catalog upstream Conformist for who may run; Acquisition ACL → Ingestion; Classification Shared Kernel (evidence) with Analytics; Analytics Open Host Service for UI/MCP; Research partnership with Ingestion + Analytics; Ops does **not** own topic strings.

---

## 5. Target package layout (monolith — rename gravity, not microservices)

Introduce layers **beside** current packages; migrate wave-by-wave. Final shape (after waves):

```text
backend/app/
  main.py                 # web composition root
  bootstrap.py            # shared wiring: MCP, scheduler, scripts

  domain/                 # THIN — only real invariants
    job/                  # identity keys, status transitions, evidence_tier policy
    research_intent/      # kind, soft-delete, versioning policies
    classification/       # ← promote from classification/rules (+ language_rules)
    shared_kernel/        # EvidenceTier, CLOSED_JOB_STATUSES, Money/rate VO later

  application/
    ports/
      driven/             # protocols / ABCs owned by application
        job_repository.py
        collector_gateway.py
        source_catalog.py
        credentials.py
        unit_of_work.py
        tick_store.py
        llm_gateway.py
      driving/            # optional: use-case interfaces if multiple adapters
    collection/
      run_source.py       # SINGLE path ← crawl_one + router.run_source
      daily_crawl.py      # policy from daily_crawlers
      ingest_batch.py
    research_intents/
    briefs/               # ← llm/briefs + handlers (name off “llm”)
    market_queries/       # thin facades → analytics (optional)
    alerts/

  adapters/
    driving/
      http/               # ← api/
      mcp/
      scheduler/          # loop only
      cli/
    driven/
      persistence/        # ← storage/ + SQLAlchemy repos
      collectors/         # ← collectors/
      secrets/ fx/ stats/ taxonomy/

  # Stay put until late waves (read side OK as package):
  analytics/              # SQL read models (CQRS-light)
  # transitional: research/, ingestion/, classification/ shrink as ports land

  core/                   # config, middleware, health
```

**Dependency rule:** `domain` ← `application` ← `adapters` / drivers.  
`analytics` may depend on `domain.shared_kernel` + persistence models, **not** on HTTP/MCP.

---

## 6. Ports to introduce first (deep modules)

### Driven (outbound)

| Port | Responsibility | First adapter |
|---|---|---|
| `CollectorGateway` | `collect(source_key, query) → CollectorResult` | registry + BaseCollector |
| `JobWriteRepository` | find_duplicate, save job graph, soft_expire | SQLAlchemy over current `ingestion/*` |
| `IntentMatchRepository` | upsert matches | current `upsert_intent_match` |
| `SourceCatalogPort` | ACTIVE keys / summary | `sources/catalog.py` |
| `ConnectorCredentialsPort` | presence + bundle (ATS CSV ≠ secrets) | `secrets` + credentials helpers |
| `TickStore` | UTC-day idempotency | file/redis behind current tick_state |
| `LlmGateway` | classify/eval only | `llm/provider` |

### Driving (inbound) — use cases as the port

| Use case | Merges / replaces |
|---|---|
| `RunSource` | `crawl_run.crawl_one` + `router.run_source` |
| `RunDailyCrawl` | `daily_crawlers` policy |
| `IngestBatch` | `ingest_raw_jobs` |
| `SyncResearchIntent` | `research/sync.py` |
| `RenderBrief` | `llm/briefs` dispatcher |
| `AcceptWatchSuggestion` | propose → persist intent (ADR-007) |

**YAGNI:** no Event Sourcing, no outbox, no per-KPI repository, no full CQRS write model, no microservices.

---

## 7. CQRS stance

| Question | Answer |
|---|---|
| Formal CQRS now? | **CQRS-light yes, ceremony no** |
| Why | Writes already funnel through ingestion; reads are aggregations. Separate read **packages** exist (`analytics`). Separate read **DB/models** are not justified. |
| Do | Keep `analytics/*` as SQL adapters; gate via `evidence_gate` + `lenses`; optional `MarketQueryService` facade for API/MCP |
| Don’t | Duplicate Job into “read entities”; build query buses; sync projections for every KPI |

**Research writes:** `sync` / `rematch` / `match_backfill` are **application write use cases** in Research/Ingestion — not part of analytics read models.

---

## 8. What NOT to over-engineer

- Dashboard prefs / view_mode / locale / widgets  
- FX helpers  
- Profile CRUD, alerts (until rules thicken)  
- Rich domain for every ORM table  
- Free-form LLM→SQL (forbidden by ADR-006)  
- Cartesian intent × all collectors  
- Merging Eurostat/ADEM/procurement into job rate KPIs  
- Renaming product terms for “purer DDD English”

---

## 9. Migration waves (implementation plan)

Each wave = independently mergeable PR theme; tests green; ≤500 LOC/file; no unsolicited commits.

### Wave 0 — Freeze language + seams (docs + shared kernel)

**Goal:** Stop language drift; extract shared constants without moving folders.

- [x] Add `docs/GLOSSARY.md` (or `backend/GLOSSARY.md`) with §3 terms + ADR cross-links  
- [x] ADR-008 draft: “Hexagonal + DDD incremental adoption” (ports-first, no entity rewrite)  
- [x] Move `CLOSED_JOB_STATUSES` (and similar) to `domain/shared_kernel` or `storage/enums` — **break** `ingestion → analytics` import  
- [x] Document connector triple-truth: catalog / registry / DB (alignment checklist in Ops README)  
- [x] Tests: existing suite green; add unit test that ingestion does not import `app.analytics`

**Done when:** glossary + ADR accepted; country_backfill no longer imports analytics.

---

### Wave 1 — Single `RunSource` use case (highest ROI)

**Goal:** One application path for collect → ingest → soft-expire → CollectionRun.

- [x] Extract `application/collection/run_source.py` from `scheduler/crawl_run.py`  
- [x] Make `daily_crawlers` call `RunSource` only (`crawl_one` thin alias)  
- [x] Replace `router.run_source` body with the same use case (HTTP = driving adapter)  
- [x] Optional: `CollectorGateway` protocol wrapping `get_collector` (done Wave 5)  
- [x] Tests: existing crawl_one tests + shared-kernel unit; smoke when stack ready  

**Done when:** grep shows one orchestration implementation; HTTP and scheduler share it.

---

### Wave 2 — Composition root (`bootstrap.py`)

**Goal:** MCP, scheduler, scripts, FastAPI share wiring.

- [x] `bootstrap.build_container()` → session factory + readonly factory (+ settings/engine)  
- [x] Wire FastAPI `Depends(get_app_container)` (beyond API-key deps)  
- [x] MCP handlers resolve sessions via container (`_session_factory` → readonly)  
- [x] Scheduler / daily_crawlers open sessions via container  
- [x] Tests: `test_bootstrap.py` container build + singleton  
- [x] Collectors/credentials on container (done Wave 5)  
- [x] Eliminate remaining `SessionLocal()` in `secrets/resolve` (uses `get_container().session_scope`)  

**Done when:** web/MCP/scheduler share `get_container()`; secrets path deferred.

---

### Wave 3 — Write ports for Ingestion

**Goal:** `IngestBatch` / soft-expire talk to `JobWriteRepository`, not raw Session in every helper.

- [x] Define `JobWritePort` (ingest + soft_expire); UoW remains Session for now  
- [x] SQLAlchemy adapter wrapping current `ingest_raw_jobs` / `soft_expire_source_jobs`  
- [x] `IngestBatch` / `soft_expire_batch` facades; `RunSource` takes optional `job_write`  
- [x] Wire adapter on `AppContainer.job_write`  
- [x] Promote pure helpers: soft-expire **decision** without SQL (`domain.job.soft_expire_policy`)  
- [x] Keep ORM `Job` as persistence model (no dual entity yet)  
- [x] Tests: fake `JobWritePort` + crawl summary patches  

**Done when:** crawl path goes through the port; deep rewrite of `ingestion/service.py` deferred.

---

### Wave 4 — Classification as domain package

**Goal:** Make purity obvious and importable without storage.

- [x] Promote via `domain/classification` facade (`classify_job`, language rules, TAXONOMY)  
- [x] Taxonomy catalog remains data under `classification/`; ensure stays in ingestion  
- [x] LLM classify = application use case + `LlmGateway` (ops-driven)  
- [x] Tests: domain facade + existing classification suite  

**Done when:** domain classify has zero SQLAlchemy imports (already true — preserve).

---

### Wave 5 — Acquisition ports (collectors)

**Goal:** Testable registry/credentials without loading all adapters at import if feasible.

- [x] `CollectorGateway` + `RegistryCollectorGateway` on `AppContainer.collectors`  
- [x] `ConnectorCredentialsPort` with ATS-CSV vs secrets semantics documented  
- [x] `SourceCatalogPort` over `catalog.json`  
- [x] Fix reverse dependency: country helpers → `normalization/country_codes`; collectors must not import `ingestion`  
- [x] Tests: gateway modes + no collector→ingestion imports  

**Done when:** `arbetsformedlingen` (and peers) have no `app.ingestion` imports.

---

### Wave 6 — Research intents application slice

**Goal:** Sync/rematch/accept-watch as explicit use cases; CRUD stays thin. Research is a **mixed** BC (Explore reads + match/sync commands).

- [x] `SyncResearchIntent`, `RematchIntent`, `AcceptWatchSuggestion` under `application/research_intents`  
- [x] API `research.py` becomes driving adapter only (move SearchQuery CRUD rules out of the route)  
- [x] Point Explore (`jobs_search` / `jobs_facets`) at shared `lenses` / corpus helpers — delete duplicated scope SQL  
- [x] Preserve ADR-007 budgeted fan-out and match provenance  
- [x] Tests: sync with fake collectors; match uniqueness; Explore lens parity with market analytics  

**Done when:** research write paths do not live as route-local scripts; one lens implementation.

---

### Wave 7 — Briefs + MCP decoupling

**Goal:** Dual drivers, one application service; kill HTTP→MCP imports.

- [x] Move `llm/briefs*` → `application/briefs`  
- [x] `assistant` and MCP both call `RenderBrief`  
- [x] MCP keep schema validate/propose as application or shared; HTTP must not import `app.mcp`  
- [x] `adapters/driven/llm_provider` for real LLM I/O only  
- [x] Tests: brief handlers; assistant API smoke  

**Done when:** `rg "from app.mcp" backend/app/api` is empty.

---

### Wave 8 — Analytics facade (optional CQRS-light)

**Goal:** Stable query surface for API/MCP without rewriting SQL. Formal CQRS (projected read DB) stays **out of scope**.

- [x] Optional `application/market_queries` facades wrapping `kpis`, `lenses`, matrices  
- [x] Split `kpis.py` / `market_extra.py` if still near 500 LOC (file-size rule) — both under 450; deferred  
- [x] Keep Session inside analytics adapters; do not invent read repositories per metric  
- [x] Optional thin ports only for **Stats External**: `ExternalStatsGateway` (eurostat/adem/fx/taxonomy) — mockable HTTP  
- [x] Tests: API smoke + evidence_gate defaults unchanged  

**Done when:** new endpoints call facades; evidence-first defaults unchanged (ADR-001).

---

### Wave 9 — Job domain entity (only if needed)

**Gate:** Start only when status FSM / canonical merge / skill-set invariants are painful to enforce in services.

- [ ] ~~Introduce `domain/job/Job` aggregate~~ — **deferred (gate not met)**  
- [ ] Mapper in persistence adapter  
- [ ] Analytics still queries ORM/SQL  
- [ ] Tests: invariant unit tests + one ingest integration  

**Done when:** write invariants live in domain; read path untouched.  
**Status (2026-10-23):** Skipped — ORM `Job` + soft-expire policy suffice; revisit if merge/status FSM pain appears.

---

## 10. Suggested PR slicing (themes)

| PR theme | Waves | Risk |
|---|---|---|
| A — Shared kernel + glossary + ADR-008 | 0 | Low |
| B — RunSource unification | 1 | Medium (crawl behavior) |
| C — bootstrap / DI | 2 | Medium |
| D — Ingestion ports | 3 | Medium |
| E — Classification promote | 4 | Low |
| F — Collector ports + reverse-dep fix | 5 | Medium |
| G — Research use cases | 6 | Medium |
| H — Briefs/MCP decoupling | 7 | Medium |
| I — Analytics facades / splits | 8 | Low |
| J — Job entity (optional) | 9 | High — defer |

Keep **separate** from frontend FSD and IT/CH/LU source PRs (same rule as before).

---

## 11. Verification bar (every wave)

- [x] `pytest` for touched packages  
- [x] `backend/scripts/smoke_e2e.sh` (or compose relaunch smoke) when crawl/ingest/API touched  
- [x] No new file > 500 LOC; split before append  
- [x] No ADR-001/003/007 regressions (evidence defaults, authorized connectors, lens/match semantics)  
- [x] Import direction check: `domain` does not import `adapters` / `api` / `mcp`

---

## 12. Closeout (2026-10-23)

Waves **0–8 complete**; Wave **9 deferred** (ORM `Job` + soft-expire policy suffice).

Remaining optional polish (not blocking):
- Point more MCP tools at `application/market_queries` as endpoints grow
- Split `kpis.py` / `market_extra.py` only if they approach 500 LOC
- Introduce Wave 9 Job aggregate only when status FSM / canonical merge hurts

Ship as PR themes A–I from §10; keep separate from frontend FSD and IT/CH/LU source PRs.
