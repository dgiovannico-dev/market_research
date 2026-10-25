# Architecture overview

**Bottom line:** FMI is a full-stack pipeline that ingests **authorized** job listings, stores them in PostgreSQL with explicit evidence metadata, classifies skills/rates/certs, and serves **observed** KPIs to the Atlas UI and optional MCP tools. Numbers on screen are row counts in *this* database—not estimates of total market size ([ADR-001](../decisions/ADR-001-evidence-first-kpis.md)).

## Who it is for and what it solves

Freelance Market Intelligence (FMI) targets **IT freelancers and operators** who need defensible demand signals: which skills, rates, geographies, and certifications show up in real postings they can cite. The product problem is not “predict the market” but **collect, normalize, and explain what was actually observed** from approved connectors, then slice that corpus by research intents (Demand Compass) and personal focus. The Next.js Atlas app (EN/IT) is grouped into four nav zones—Explore, Jobs, Ops, Research—defined in `frontend/lib/navZones.ts`; see [manuals/OVERVIEW.md](../manuals/OVERVIEW.md) for route-level guidance.

## System containers (C4-style)

Runtime pieces and trust boundaries:

```mermaid
flowchart TB
  subgraph users["People"]
    U[Freelancer / analyst]
    OP[Operator / admin]
  end

  subgraph fmi["FMI deploy boundary"]
    FE["Browser · Next.js Atlas<br/>OIDC PKCE · localStorage profile"]
    API["API · FastAPI<br/>REST /api/v1 · OpenAPI /docs"]
    SCH["Scheduler · in-process or CronJob<br/>daily crawlers + RunSource"]
    MCP["MCP · stdio analytics<br/>not HTTP"]
    PG[(PostgreSQL 16<br/>system of record)]
    VK[(Valkey · Redis protocol<br/>cache / rate limits)]
  end

  subgraph external["External"]
    KC[Keycloak OIDC]
    LLM[LLM provider optional<br/>Ollama / OpenAI-compatible / Gemini]
    SRC[Authorized job sources<br/>HTTP APIs · feeds · dumps]
  end

  U --> FE
  OP --> FE
  OP --> API
  FE -->|Bearer JWT| API
  FE -->|OIDC login| KC
  API -->|JWT validation| KC
  API --> PG
  API --> VK
  API -.->|admin runtime| LLM
  SCH --> API
  SCH --> PG
  API --> SRC
  MCP -->|readonly SQL| PG
  OP --> MCP
```

| Container | Role |
|-----------|------|
| Browser (Next.js) | Atlas UI, dashboard prefs, profile in **localStorage** ([ADR-009](../decisions/ADR-009-keycloak-identity-localstorage-profile.md)) |
| API (FastAPI) | HTTP drivers, analytics reads, ops, assistant hooks |
| PostgreSQL 16 | Jobs, intents, sources, LLM admin, outcomes |
| Valkey | `REDIS_URL` cache and rate limiting when configured |
| Keycloak | OIDC IdP; roles `user` / `admin` — [ops/KEYCLOAK.md](../ops/KEYCLOAK.md) |
| LLM (optional) | Classification refine, briefs, study advisor; DB-backed runtime ([ADR-010](../decisions/ADR-010-admin-llm-runtime-config.md)) |
| MCP (stdio) | Schema-driven metrics/briefs for agents — not exposed as HTTP ([ADR-006](../decisions/ADR-006-mcp-schema-driven-analytics.md)) |

**Run locally:** Docker Compose — [ops/LOCAL.md](../ops/LOCAL.md). **Production-shaped:** Helm on k3s — [ops/HELM-k3s.md](../ops/HELM-k3s.md). **Incidents:** [ops/RUNBOOKS.md](../ops/RUNBOOKS.md). **Releases:** [ops/RELEASE.md](../ops/RELEASE.md).

## Product modules

Backend and UI features map to these bounded capabilities (names match code and docs):

| Module | Responsibility |
|--------|----------------|
| **sources** | Global catalog (`data/sources/catalog.json`); only **ACTIVE** connectors ingest ([ADR-003](../decisions/ADR-003-authorized-connectors-only.md), [ADR-005](../decisions/ADR-005-global-source-catalog.md)) |
| **research-intents** | Demand Compass: **discovery** and **focus** `SearchQuery` rows; lenses and provenance ([ADR-007](../decisions/ADR-007-query-first-sync.md)) |
| **ingest** | Collectors → `RawJob` → upsert jobs, skills, rates, certs |
| **classify** | Modes `rules` \| `hybrid` \| `llm`; evidence kinds on facts ([ADR-002](../decisions/ADR-002-classification-modes.md)) |
| **analytics** | SQL read adapters (summary, trends, rates, geo, co-occurrence, certs) |
| **dashboard** | Signal desk UI; **guided** vs **trends_only** presentation ([ADR-004](../decisions/ADR-004-dashboard-modes.md)) |
| **profile-outcomes** | Applications, alerts, weekly report; server profile is seed-oriented |
| **stack-compass** | Learning candidates / irreplaceability from profile + market |
| **study-advisor** | Evidence-grounded study plans, busy-slot / ICS week calendar, WLB distribution (optional LLM refine) |
| **certifications** | Taxonomy + job↔cert KPIs |
| **ops** | Scheduler, credentials, LLM runtime/prompts, metrics |
| **mcp-analytics** | Stdio MCP for schema/metrics/briefs |

## Hexagonal layout (backend)

Adoption is **incremental and ports-first** ([ADR-008](../decisions/ADR-008-hexagonal-ddd-incremental.md)). `bootstrap.py` builds `AppContainer`: settings, SQLAlchemy sessions (including optional readonly URL), and driven adapters (collectors, catalog, credentials, job write, LLM factory, external stats). Web, scheduler, MCP, and scripts share this composition root instead of opening ad hoc DB connections.

```mermaid
flowchart TB
  subgraph drivers["Driving adapters"]
    HTTP["api/v1 · FastAPI routes"]
    CRON["scheduler/ · daily crawlers"]
    CLI["scripts · smoke / maintenance"]
  end

  subgraph app["Application core"]
    UC["application/ · use cases"]
    PORTS["application/ports/driven · interfaces"]
    DOM["domain/ · pure rules<br/>classification · intent policies"]
  end

  subgraph driven["Driven adapters"]
    SQL["adapters/driven/persistence"]
    COLL["adapters/driven/collectors + collectors/"]
    CAT["adapters/driven/catalog"]
    CRE["adapters/driven/credentials"]
    LLMA["adapters/driven/llm"]
    STATS["adapters/driven/stats"]
  end

  subgraph infra["Infrastructure"]
    STOR["storage/ · ORM models"]
    ING["ingestion/ · write path"]
    ANA["analytics/ · SQL reads"]
    AUTH["auth/ · OIDC JWT"]
    MCPM["mcp/ · stdio tools"]
  end

  HTTP --> UC
  CRON --> UC
  CLI --> UC
  UC --> PORTS
  UC --> DOM
  PORTS --> SQL
  PORTS --> COLL
  PORTS --> CAT
  PORTS --> CRE
  PORTS --> LLMA
  PORTS --> STATS
  SQL --> STOR
  ING --> STOR
  ANA --> STOR
  COLL --> ING
```

**Layout on disk:**

```
backend/app/
  api/v1/           # HTTP drivers
  application/      # use cases + driven ports
  adapters/driven/  # SQLAlchemy, collectors registry, catalog, LLM, credentials
  domain/           # thin pure rules
  collectors/       # connector adapters → RawJob
  ingestion/        # write path into Postgres
  analytics/        # SQL read adapters (CQRS-light)
  storage/          # ORM models (split modules; barrel models.py)
  bootstrap.py      # AppContainer composition root
  auth/             # OIDC JWT
  mcp/, scheduler/, reports/
```

**Hard rules:** one crawl path (`RunSource` for HTTP run and daily tick); analytics stay SQL read adapters; HTTP must not import `app.mcp`.

## End-to-end flow (tick → UI)

Scheduled work and user reads share the same corpus. Analytics never invent rows—they query Postgres with lens filters (`market` \| `focus` \| `compare`).

```mermaid
sequenceDiagram
  participant Sched as Scheduler / cron
  participant DC as daily_crawlers
  participant RS as RunSource
  participant Coll as Collectors
  participant Ing as ingestion
  participant Cls as classify + certs
  participant PG as PostgreSQL
  participant Ana as analytics
  participant API as FastAPI
  participant FE as Next.js Atlas

  Sched->>DC: UTC-day tick (budgeted)
  DC->>RS: dump / feed then discovery then focus
  Note over DC,RS: No silent env topic defaults (ADR-007)
  RS->>Coll: fetch per ACTIVE source
  Coll-->>RS: RawJob stream
  RS->>Ing: normalize · dedup · evidence_tier
  Ing->>PG: upsert jobs · job_intent_matches · skills · rates
  Ing->>Cls: classify mode rules/hybrid/llm
  Cls->>PG: job_skills · job_certifications · metadata

  FE->>API: GET /api/v1/... (lens · filters)
  API->>Ana: KPI SQL (min_evidence default)
  Ana->>PG: read corpus
  PG-->>Ana: rows + counts
  Ana-->>API: KPI + coverage_notes
  API-->>FE: JSON charts / tables
```

**Stages in plain language:**

1. **Tick** — Dump/feed collectors run first, then discovery watchlist, then focus intents. Intents drive *what* to crawl; env does not silently substitute topics ([ADR-007](../decisions/ADR-007-query-first-sync.md)).
2. **Ingest** — Normalize URLs and text, resolve duplicate groups, set `evidence_tier`, attach **`job_intent_matches`** (normative provenance; `jobs.query_id` is supporting).
3. **Classify** — Rules, hybrid, or LLM paths attach technologies, contract/remote evidence, certification links.
4. **Read** — Dashboards, assistant, and MCP query the same tables with lens and quality gates ([DATABASE.md](DATABASE.md)).

## Auth and actors

Identity is split: **Keycloak** for who can call the API; **localStorage** for end-user career profile data on the device ([ADR-009](../decisions/ADR-009-keycloak-identity-localstorage-profile.md)).

```mermaid
flowchart LR
  subgraph browser["Browser"]
    FE[Next.js]
    LS[(localStorage profile<br/>dashboard prefs)]
  end

  subgraph api["API"]
    OIDC[JWT validation]
    KEY[X-Api-Key]
    OPS[X-Ops-Token]
  end

  KC[Keycloak]
  FE -->|Authorization Code + PKCE| KC
  FE -->|Bearer access_token| OIDC
  FE --> LS
  Cron[Cron / smoke scripts] -->|API_KEY| KEY
  Break[Break-glass admin] -->|when OIDC enabled| OPS
```

| Actor | Mechanism | Typical use |
|-------|-----------|-------------|
| Browser user | OIDC Bearer (`user` or `admin`) | Atlas UI, authenticated API |
| Cron / smoke | `X-Api-Key` (`API_KEY`) | Scheduled crawls, CI smoke |
| Break-glass admin | `X-Ops-Token` when OIDC is on | Emergency ops without IdP |
| End-user profile | **localStorage** (not server multi-tenant identity) | Skills, prefs, applications UX |

## Architecture decision index

| ADR | One-line summary |
|-----|------------------|
| [001](../decisions/ADR-001-evidence-first-kpis.md) | Observed row counts ≠ total market size |
| [002](../decisions/ADR-002-classification-modes.md) | `rules` / `hybrid` / `llm` classification |
| [003](../decisions/ADR-003-authorized-connectors-only.md) | No ToS bypass; ACTIVE gate for ingest |
| [004](../decisions/ADR-004-dashboard-modes.md) | Guided vs trends-only presentation |
| [005](../decisions/ADR-005-global-source-catalog.md) | JSON catalog is SoR for source candidates |
| [006](../decisions/ADR-006-mcp-schema-driven-analytics.md) | Validated specs, not free SQL in UI |
| [007](../decisions/ADR-007-query-first-sync.md) | Discovery + focus intents; analytics lenses |
| [008](../decisions/ADR-008-hexagonal-ddd-incremental.md) | Hexagonal ports/adapters, incremental |
| [009](../decisions/ADR-009-keycloak-identity-localstorage-profile.md) | Keycloak + localStorage profile |
| [010](../decisions/ADR-010-admin-llm-runtime-config.md) | DB LLM runtime + prompt registry |

Ubiquitous terms: [GLOSSARY.md](../GLOSSARY.md).

## Related documentation

| Topic | Document |
|-------|----------|
| Schema, tiers, migrations | [DATABASE.md](DATABASE.md) |
| Doc hub | [README.md](../README.md) |
| Using the app | [manuals/OVERVIEW.md](../manuals/OVERVIEW.md), [EXPLORE](../manuals/EXPLORE.md), [CAREER](../manuals/CAREER.md), [RESEARCH](../manuals/RESEARCH.md), [ADMIN](../manuals/ADMIN.md) |
| Local stack | [ops/LOCAL.md](../ops/LOCAL.md) |
| Kubernetes deploy | [ops/HELM-k3s.md](../ops/HELM-k3s.md) |
| OIDC setup | [ops/KEYCLOAK.md](../ops/KEYCLOAK.md) |
