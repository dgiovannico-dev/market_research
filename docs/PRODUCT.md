# Product: Freelance Market Intelligence (FMI)

## Objective

Help senior IT freelancers—especially AI & backend specialists—act as if they had a **Demand Compass**: decide which technologies show **strong observed demand**, which signals are **rising or cooling**, and **where** demand concentrates (geo / remote), using **observed job records** plus an LLM that **interprets evidence**—never invents market size.

Build a **global, continuously expandable** base of IT / freelance / contractor market data by verifying and integrating authorized sources (APIs, feeds, ATS boards, official datasets, structured imports)—never inventing access, licenses, or test results.

Success looks like:

- **Market radar on day one:** Executive/Trends answer “what’s hot / cooling / where?” from a transparent **Discovery watchlist** + dump/feed corpus—not from a hidden env `java` default, and not only from what the user already typed.
- **Personal focus without echo chamber:** user saves **Focus intents** for deep dives; Compare lens shows my bets vs market.
- Explore searches the **DB first**; optional refresh re-collects with explicit text/intent.
- LLM briefs (rising/cooling, geo, adjacent skills, focus-vs-market, suggested watches with **accept**) grounded in DB `n=` and limits.
- UI in **Italian and English**; Executive/Trends as a **chart-forward signal desk** (rising/cooling hero, sparklines, compare dual-series)—beautiful empty states when the corpus is thin, never fake charts.
- User can inspect the source catalog with honest verification status; guided vs trends-only presentation; customizable widgets/nav.
- User never confuses “jobs in this DB” with “total market demand.”

## Target persona

**Senior AI & Backend Engineer** — Enterprise RAG · LLM Integration · Java & Python · Cloud Architecture.

### Professional profile (summary)

Designs and integrates generative AI in enterprise settings: RAG pipelines, LLM runtimes (Ollama, vLLM, OpenAI-compatible APIs), FastAPI/Python backends, REST/microservices, cloud-ready deployment, evaluation, guardrails, and operational sustainability.

### Priority professions (persona examples — not the sync control plane)

These describe the **target user**. Market radar uses the transparent **Discovery watchlist** (`data/research/discovery_watchlist.json`); personal deep dives use **Focus intents**. Neither lives as silent `*_DEFAULT_QUERY` in env ([SPEC-research-intents.md](specs/SPEC-research-intents.md), [ADR-007](decisions/ADR-007-query-first-sync.md), [Demand Compass](ideas/freelance-demand-compass.md)).

- Senior Java Engineer / Spring Boot Developer
- Backend and Full-Stack Engineer
- Cloud, Platform, and DevOps Engineer
- Software Architect and Technical Lead
- AI / Generative AI / LLM / RAG / AI Agent Engineer
- Data Engineer and Machine Learning Engineer
- Freelance IT Consultant / Independent Contractor
- Enterprise AI Architect / AI Platform Engineer

### Geography

**Worldwide** scope. Live connectors today are remote-global and DE/EU-biased; national PES, UK boards, and marketplaces need credentials—see [sources/COVERAGE_GAPS.md](sources/COVERAGE_GAPS.md).

### Decisions FMI must support

| Decision | FMI signal |
|----------|------------|
| Which skills are rising in observed demand? | Trends, co-occurrence |
| Where are rates advertised (when present)? | Rates analytics (NULL if missing) |
| Which countries appear in remote/EU roles? | Countries breakdown |
| How does my skill set compare to observed demand? | Profile skill gaps (guided mode) |
| What should I track weekly? | Alerts + weekly report |
| Do I want advice or just charts? | `guided` vs `trends_only` |
| Which sources feed the DB and what is missing? | Sources catalog + coverage gaps |
| Can I describe a view and get a dashboard/report? | MCP / assistant → validated DashboardSpec / ReportSpec |
| What’s rising or cooling in observed demand? | Trends / LLM `rising_cooling` brief (lens=`market`) |
| Where is demand stronger for a skill? | Countries + LLM `where_demand` |
| How do my bets compare to the market? | Focus intents + Compare lens / `focus_vs_market` |
| How is the DB kept fresh? | **Daily crawlers** over authorized sources (cron → collectors) |
| What should daily crawlers fetch? | Discovery watchlist + My focus intents — not env topic defaults |

### Technologies in this product (in-repo)

Backend: Python, FastAPI, PostgreSQL, SQLAlchemy, Alembic, Docker Compose, CI.  
AI: rules / hybrid / LLM classification; Ollama & vLLM providers.  
Frontend: Next.js, Tailwind.  
Sources: modular collectors, FX (Frankfurter/ECB), catalog seed sync.

### Out of current product stack (roadmap only)

Java/Spring Boot services, full Kubernetes, OAuth2/OIDC IdP, enterprise vector DB RAG — see [ROADMAP.md](ROADMAP.md) Later. Do not claim them as shipped.

## Global sources (product requirement)

Categories A–I (aggregators, freelance marketplaces, agencies, ATS, official stats, salary surveys, FX/taxonomies, procurement, discovery aids) are tracked in [`data/sources/catalog.json`](../data/sources/catalog.json).

Rules:

- Catalog entry ≠ integrated source.
- `ACTIVE` only after a connector returns real records under test.
- No scraping that bypasses auth, CAPTCHA, paywall, or ToS ([ADR-003](decisions/ADR-003-authorized-connectors-only.md), [SPEC-sources.md](specs/SPEC-sources.md)).
- Keep salary employee vs freelance hourly/daily/monthly vs project budget vs undeclared **separate**; never invent missing rates.
- Do not equate procurement contract value with a professional day rate.
- Do not sum incomparable national statistics series.

Deliverable docs: [sources/VALIDATION_REPORT.md](sources/VALIDATION_REPORT.md), [sources/COVERAGE_GAPS.md](sources/COVERAGE_GAPS.md).

## Value proposition

- **Evidence-first:** every KPI carries definition, sample size, evidence kind, and limits (in guided mode).
- **Honest coverage:** global catalog with verification statuses; gaps explicit.
- **Customizable:** preferences for widgets, time window, tech/country focus, nav visibility, saved presets.
- **Dual presentation:** guided coaching vs clean trends for power users.
- **Legal by design:** only authorized/public connectors; unsupported sources stay non-runnable.

## Dashboard modes

Modes are product-level and **configurable**. They are not mutually exclusive across the product (a user may keep both pages); each view renders according to `view_mode`.

### 1. Guided / evidence mode (default)

- KPI cards with definition, limits, evidence_kind, disclaimer.
- Growth status and methodology copy.
- Skill-gap and positioning recommendations when profile is set.
- Quality/coverage cues.

Reference UX today: Executive, Profile, Report pages.

### 2. Trends-only / minimal mode

- Charts/tables of observed trends only.
- **No** long disclaimers, definition/limits blocks, or positioning recommendations.
- Short labels allowed (metric name, n=, period). Numbers remain from observed data only.
- Primary surfaces: Trends page + optional minimal Executive strip.

### Customization (product requirements)

Persist preferences (v1: `localStorage`; v1.1: profile API):

| Preference | Values |
|------------|--------|
| `view_mode` | `guided` \| `trends_only` |
| `locale` | `it` \| `en` |
| `period_days` | e.g. 30, 90, 180 |
| `visible_widgets` | set of widget ids |
| `focus_technologies` | string list |
| `focus_countries` | ISO codes |
| `nav_hidden` | route list to hide |
| `presets` | named snapshots of the above |

Example presets: “RAG/LLM demand”, “Rates EU”, “Solo trends”.

Acceptance for trends-only is detailed in [specs/SPEC-dashboard.md](specs/SPEC-dashboard.md) and [decisions/ADR-004-dashboard-modes.md](decisions/ADR-004-dashboard-modes.md).

## MCP-assisted dashboards & reports

An MCP server (`mcp-analytics`, `python -m app.mcp`) exposes schema metadata and a semantic metric catalog so an LLM (Cursor agent or in-app Assistant) can interpret a user prompt and emit a **validated** dashboard or report spec, grounded with read-only queries / existing analytics APIs. Demand Compass briefs use the same evidence path via `render_demand_brief` (suggest watches never auto-INSERT). In-app bridge: `POST /api/v1/assistant/propose` + `/assistant/brief`.

- Spec: [specs/SPEC-mcp-analytics.md](specs/SPEC-mcp-analytics.md)
- ADR: [decisions/ADR-006-mcp-schema-driven-analytics.md](decisions/ADR-006-mcp-schema-driven-analytics.md)
- Plan: [superpowers/plans/2026-10-20-mcp-schema-dashboards.md](superpowers/plans/2026-10-20-mcp-schema-dashboards.md)
- Cursor wiring: [mcp/CURSOR.md](mcp/CURSOR.md) (optional confirm of `.cursor/mcp.json` still in Next)

Distinct from RAG over job text ([ROADMAP.md](ROADMAP.md) Later): MCP composes **structured** KPIs; RAG answers from descriptions.

## Demand Compass (discovery + focus)

FMI’s product framing is a **Demand Compass**: discover market signals, then deepen personal focus—without silent env topic defaults and without a confirmation-bias “query-only” corpus.

Corpus paths (in product today):

1. **Discovery (market scan)** — versioned probes in [`data/research/discovery_watchlist.json`](../data/research/discovery_watchlist.json), seeded as `SearchQuery.kind=discovery` (visible, disableable in UI).
2. **Focus (my bets)** — user-typed intents (`kind=focus`) for personal positioning (`/focus`).
3. **Dump/feed** — board/RSS sync once per daily tick (unlabeled background).

**Daily crawlers** (scheduled, once per day in production) refresh the corpus: dump/feed → budgeted discovery → budgeted focus via authorized collectors only. Intent hits are stored in **`job_intent_matches`** so a job can serve both market and focus lenses. Search APIs **never** invent topics from env (`*_DEFAULT_QUERY` deprecated). Dashboards/LLM read Postgres—they do not crawl on page view. Per-intent Sync / Sources “Run” are optional ops supplements. Analytics lenses: `market` (default in UI) / `focus` / `compare` — `LensToggle` on Executive, Trends, Jobs, Skills, Quality (and Rates/Countries/Assistant). LLM brief APIs propose watches; user **accepts** before crawlers include them (`WatchCandidates` → `POST /research/watches/accept`). UI chrome is **IT/EN** (`next-intl`) with chart-forward Executive/Trends. Assistant propose/briefs pass `locale` and echo `meta.locale` / `meta.narrative_locale`; **evidence narratives stay English (MVP)**. Ops walkthrough: [ops/demand-compass-walkthrough.md](ops/demand-compass-walkthrough.md); smoke: `backend/scripts/smoke_compass.sh` (CI `compass-smoke`).

Shipped on `/assistant`: brief-type chips (`DemandCompassSection`) + accept-watch UX. SPEC-i18n / SPEC-dashboard MVP acceptance signed off. Not claimed (Later): Italian evidence narratives (`meta.narrative_locale` beyond fixed `en`).

**Evidence quality (DSS):** jobs carry `evidence_tier` (`standard`|`thin`). Skills, rates, trends, and briefs default to `min_evidence=standard` (thin/capped sources stay in inventory and Quality `by_source.pct_thin`). Soft-expired (`closed_stale`) jobs leave the analytics corpus. See [ADR-001](decisions/ADR-001-evidence-first-kpis.md).

Tech review: [reviews/2026-10-20-demand-compass-tech-review.md](reviews/2026-10-20-demand-compass-tech-review.md).

Docs: [ideas/freelance-demand-compass.md](ideas/freelance-demand-compass.md) · [ideas/demand-compass-experience.md](ideas/demand-compass-experience.md) · [specs/SPEC-research-intents.md](specs/SPEC-research-intents.md) · [specs/SPEC-i18n.md](specs/SPEC-i18n.md) · [specs/SPEC-dashboard.md](specs/SPEC-dashboard.md) · [decisions/ADR-007-query-first-sync.md](decisions/ADR-007-query-first-sync.md) · [plans](superpowers/plans/2026-10-20-query-first-daily-sync.md) · [i18n/visual plan](superpowers/plans/2026-10-20-i18n-and-visual-dashboard.md).

## Non-goals

- Inventing total market size or filling missing rates with zeros.
- Silent product topic defaults via `*_DEFAULT_QUERY` / similar env keys.
- Syncing **only** what the user already typed (confirmation-bias “query-only” product).
- Auto-enabling LLM-suggested watches without accept.
- Scraping that bypasses auth, CAPTCHA, paywall, or ToS.
- Declaring a source integrated without a working connector and real data.
- Letting an LLM run arbitrary write SQL or ship unvalidated UI code.
- Replacing a personal CRM for all applications (FMI tracks outcomes lightly).
- Shipping enterprise RAG in the same slice as dashboard customization (separate plan).

## Related docs

- Capability map: [CAPABILITY_MAP.md](CAPABILITY_MAP.md)
- Master spec: [SPEC.md](SPEC.md)
- Sources spec: [specs/SPEC-sources.md](specs/SPEC-sources.md)
- Research intents: [specs/SPEC-research-intents.md](specs/SPEC-research-intents.md)
- MCP analytics: [specs/SPEC-mcp-analytics.md](specs/SPEC-mcp-analytics.md)
- Roadmap: [ROADMAP.md](ROADMAP.md)
