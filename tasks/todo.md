# Task list: FMI next slices

Docs phase (PRODUCT, SPEC*, ADRs, sources registry, plans) is complete for the global sources baseline. Implement below in order unless noted parallel-safe.

---

## Task 1: Dashboard preferences store

**Acceptance criteria:**
- [x] Type-safe defaults; soft-fail when storage unavailable
- [x] Key namespaced `fmi:dashboardPrefs:v1`

**Verification:**
- [x] `npm run build`

---

## Task 2: Mode toggle + provider

**Acceptance criteria:**
- [x] Toggle updates `view_mode` and persists
- [x] Available from main layout (`AppChrome`)

---

## Task 3: Trends-only rendering

**Acceptance criteria:**
- [x] `trends_only`: no disclaimer/definition/limits sections on Executive
- [x] Values + tables + `n=` remain
- [x] `guided`: evidence UX preserved

---

## Task 4: Nav hide, filters, presets

**Acceptance criteria:**
- [x] Hidden nav items not linked
- [x] Period/focus affect Executive/Trends fetches & lists
- [x] Preset save/load in Prefs panel

---

## Checkpoint: After Tasks 1–4

- [x] Guided and trends-only both usable
- [x] Prefs survive refresh (localStorage)
- [x] Frontend build green
- [x] No API contract break
- [x] `/assistant` + Apply DashboardSpec

---

## Task 5: External scheduler script + docs

**Acceptance criteria:**
- [x] `backend/scripts/scheduler_tick.sh` with optional `API_KEY`
- [x] PRODUCTION.md recommends cron when scaled

---

## Task 6: Optional Redis rate limit

**Acceptance criteria:**
- [x] 429 when over limit (`test_rate_limit.py`)
- [x] `RATE_LIMIT_BACKEND=memory|redis` + fallback
- [x] `.env.example` updated

---

## Task 7: Ops metrics endpoint

**Acceptance criteria:**
- [x] `GET /api/v1/ops/metrics` observed counts only
- [x] Smoke script includes it

---

## Checkpoint: After Tasks 5–7

- [x] pytest green for rate limit + ops metrics
- [x] PRODUCTION.md accurate
- [x] Sources catalog UI filters (Task 13)

---

## Task 8: Gold-label eval UI (Later/Next)

**Description:** Beyond rules self-consistency—dataset labels and simple agreement report.

**Acceptance criteria:**
- [x] Documented in SPEC-classify update
- [x] UI or API to run scored eval (`POST /api/v1/llm/evaluation/gold` + Quality button)
- [x] Seed dataset `data/eval/gold_labels.json` + `test_gold_eval.py`

**Dependencies:** Checkpoint after 1–4 preferred  
**Estimated scope:** L (break further when started)

---

## Task 8b: Profile dashboard prefs sync

**Acceptance criteria:**
- [x] Alembic `0003_profile_dashboard_prefs`
- [x] `GET|PUT /api/v1/profile/dashboard-prefs`
- [x] PrefsPanel Load/Save to profile (localStorage remains primary)

---

## Task 9: RAG knowledge layer (Later)

**Description:** Only after ROADMAP promotion and SPEC-rag-knowledge exists.

**Dependencies:** Explicit prioritization  
**Detail plan:** [docs/superpowers/plans/2026-10-20-rag-knowledge-layer.md](../docs/superpowers/plans/2026-10-20-rag-knowledge-layer.md)  
**Estimated scope:** XL — split per that plan

---

## Task 10: Adzuna connector (when credentials available)

**Description:** Implement Adzuna collector with env keys; live test; mark catalog `ACTIVE`.

**Acceptance criteria:**
- [x] Secrets only via env (`ADZUNA_APP_ID` / `ADZUNA_APP_KEY`)
- [x] Connector scaffold registered; fails closed without keys
- [ ] Real jobs persisted; dedup mapped (needs live keys)
- [ ] Tests + VALIDATION_REPORT + COVERAGE_GAPS updated after live run
- [ ] Catalog status `ACTIVE` only after evidence (stays `NEEDS_CREDENTIALS` until keys + live)

**Dependencies:** Real Adzuna app id/key  
**Estimated scope:** M  
**Plan:** [docs/superpowers/plans/2026-10-20-global-sources.md](../docs/superpowers/plans/2026-10-20-global-sources.md) Slice A

---

## Task 11: USAJOBS connector (when credentials available)

**Description:** US federal IT postings via official API.

**Acceptance criteria:**
- [x] Secrets only via env (`USAJOBS_API_KEY` + `USAJOBS_USER_AGENT`)
- [x] Connector scaffold registered; fails closed without keys
- [ ] Real jobs persisted; dedup mapped (needs live keys)
- [ ] Catalog `ACTIVE` only after live evidence

**Dependencies:** USAJOBS API key  
**Estimated scope:** M

---

## Task 12: Reed + EU PES connectors (when credentials available)

**Description:** Reed (UK); France Travail / Bundesagentur as keys allow.

**Acceptance criteria:**
- [x] Reed scaffold (`REED_API_KEY`); fails closed; ACTIVE gate unchanged
- [x] France Travail / Bundesagentur scaffolds (env credentials; docs + fail-closed tests)
- [ ] Live keyed runs → ACTIVE + coverage gaps update

**Dependencies:** Provider credentials / partner access  
**Estimated scope:** L

---

## Task 13: Sources catalog UI filters

**Acceptance criteria:**
- [x] `CatalogBrowser` filters by status/category via catalog API
- [x] Non-ACTIVE never presented as runnable

**Files:** `frontend/components/CatalogBrowser.tsx`

---

## Task 14: ATS tenant allowlist growth

**Description:** Expand Greenhouse/Lever/Ashby/SmartRecruiters configured org lists from a maintained allowlist; document in `.env.example`.

**Acceptance criteria:**
- [x] Only public board endpoints
- [x] Empty Ashby orgs remain non-runnable
- [x] Seed/docs note how to add tenants ([docs/sources/ATS_TENANTS.md](../docs/sources/ATS_TENANTS.md))
- [x] Default Greenhouse/Lever/Ashby/SmartRecruiters lists expanded in `.env.example` + Settings defaults

**Dependencies:** None  
**Estimated scope:** S

---

## Checkpoint: Sources expansion

- [x] No source marked ACTIVE without live evidence (seed no longer promotes Adzuna/USAJOBS on keys alone)
- [x] Catalog summary matches VALIDATION_REPORT narrative (scaffolds stay NEEDS_CREDENTIALS)
- [x] pytest green after each new connector
- [x] `GET /api/v1/ops/connectors` + Sources UI credentialed scaffold panel (booleans only)

---

## Task 15: MCP analytics server (metadata + tools)

**Description:** Implement `backend/app/mcp/` — schema metadata, semantic catalog, allowlisted read-only query, propose/validate `DashboardSpec` / `ReportSpec`, stdio MCP server.

**Acceptance criteria:**
- [x] Tools match [SPEC-mcp-analytics.md](../docs/specs/SPEC-mcp-analytics.md)
- [x] Non-SELECT / non-allowlisted SQL rejected
- [x] Specs with unknown metrics fail closed
- [x] Report materialization does not invent rates when sample empty
- [x] `python -m app.mcp` / `build_mcp()` starts

**Verification:**
- [x] `pytest backend/tests/test_mcp_*.py -q`
- [ ] Manual Cursor tool call optional

**Dependencies:** Analytics APIs stable; better after Tasks 1–4 for Apply-to-UI  
**Estimated scope:** L  
**Detail plan:** [docs/superpowers/plans/2026-10-20-mcp-schema-dashboards.md](../docs/superpowers/plans/2026-10-20-mcp-schema-dashboards.md) Tasks 1–6  
**ADR:** [ADR-006](../docs/decisions/ADR-006-mcp-schema-driven-analytics.md)

---

## Task 16: MCP ops docs + read-only DB

**Description:** `.env.example`, Cursor MCP install notes, PRODUCTION/SPEC-ops guidance for SELECT-only role.

**Acceptance criteria:**
- [x] No secrets in committed MCP config
- [x] `docs/mcp/CURSOR.md` (or README section) documents wiring
- [x] Read-only URL recommended

**Verification:**
- [x] Docs review

**Dependencies:** Task 15  
**Estimated scope:** S  
**Detail plan:** MCP plan Task 7

---

## Task 17: In-app assistant apply specs

**Description:** UI + `POST /api/v1/assistant/propose` to preview/apply DashboardSpec without browser speaking MCP.

**Acceptance criteria:**
- [x] `POST /api/v1/assistant/propose`
- [x] `/assistant` page with Apply to prefs
- [x] Tests `test_assistant_api.py`

**Dependencies:** Tasks 1–4 and 15  
**Estimated scope:** M  
**Detail plan:** MCP plan Task 8

---

## Task 18: Free taxonomy + EU/UK IT boards

**Acceptance criteria:**
- [x] JobTech taxonomy `GET /api/v1/taxonomy/jobtech/search` + Skills UI provider toggle (ESCO | JobTech)
- [x] DevITJobs collector (`devitjobs`, hosts uk/com) ACTIVE
- [x] NoFluffJobs collector (`nofluffjobs`, capped dump) ACTIVE — CEE B2B hourly useful for rates
- [x] Catalog regenerated (~176 sources, 19 ACTIVE)

**Verification:**
- [x] `pytest` 74 passed; frontend build green

**Blocked next:** keyed credentialed → ACTIVE; marketplace partnerships; Cursor MCP confirm; RAG Later

---

## Task 19: Reed RSS free path + Eurostat stats helper

**Acceptance criteria:**
- [x] Reed collector uses public RSS without API key; removed from CREDENTIALED_SCAFFOLDS; catalog ACTIVE
- [x] Optional `REED_API_KEY` still enables JSON API
- [x] Eurostat `GET /api/v1/stats/eurostat/series` (allowlisted datasets; reference only)
- [x] Catalog: Eurostat VALIDATED; No Fluff Jobs id 23 → duplicate of 176

**Verification:**
- [x] pytest + catalog regenerate

---

## Task 20: ATS tenant expand + Eurostat Rates UI

**Acceptance criteria:**
- [x] Expand GREENHOUSE/LEVER/ASHBY defaults after HTTP 200 probes
- [x] Cap 40 jobs per ATS tenant; Greenhouse listing without full HTML content
- [x] Eurostat panel on Rates page
- [x] Update `probe_ats_tenants.sh` + ATS_TENANTS.md
- [x] 2026-10-20 follow-up: Greenhouse 28 / Ashby 9 (gusto/pinterest/reddit/coursera/khanacademy + granola/runway); drop 404 probe defaults; catalog notes + VALIDATION_REPORT synced
- [x] 2026-10-21 ATS expand (probed live): +lyft (GH 180 jobs), +wealthfront (Lever 23), +supabase (Ashby 55); defaults GH 29 / Lever 3 / Ashby 10; VALIDATION_REPORT evidence; no SR empty-200 adds

**Verification:**
- [x] pytest + frontend build
- [x] Live HTTP probe of new tenants (200 + non-empty payload)

---

## Task 21: Get on Board (LATAM free API)

**Acceptance criteria:**
- [x] `getonbrd` collector via public search/category JSON
- [x] Catalog ACTIVE; LATAM coverage gap updated
- [x] Live test

**Verification:**
- [x] pytest + catalog regenerate

---

## Task 22: MyCareersFuture (SG) + JobUp (CH)

**Acceptance criteria:**
- [x] `mycareersfuture` free SG gov API v2 connector ACTIVE
- [x] `jobup` free Swiss public search connector ACTIVE
- [x] Coverage gaps updated (APAC SG, CH)

**Verification:**
- [x] pytest + catalog regenerate

---

## Task 23: NAV Arbeidsplassen + Landing.jobs + Kalibrr

**Acceptance criteria:**
- [x] `nav_arbeidsplassen` free Norwegian PES search ACTIVE
- [x] `landing_jobs` free EU tech JSON (EUR salaries) ACTIVE
- [x] `kalibrr` free SEA job board search ACTIVE
- [x] Coverage gaps updated (NO, PT/EU, SEA)

**Verification:**
- [x] pytest + catalog regenerate

---

## Task 24: DOU.ua + Authentic Jobs + Wantedly

**Acceptance criteria:**
- [x] `dou_ua` free UA IT category RSS ACTIVE
- [x] `authentic_jobs` FeedBurner jobs RSS ACTIVE (not editorial site /rss)
- [x] `wantedly` free Japan projects JSON ACTIVE

**Verification:**
- [x] pytest + catalog regenerate

---

## Task 25: Duunitori + Jobindex + Wanted + Instahyre + Hasjob

**Acceptance criteria:**
- [x] `duunitori` free FI jobentries JSON ACTIVE
- [x] `jobindex` free DK RSS ACTIVE
- [x] `wanted` free KR jobs JSON ACTIVE
- [x] `instahyre` + `hasjob` free India JSON ACTIVE
- [x] Coverage gaps updated (Nordics FI/DK, KR, IN)

**Verification:**
- [x] pytest + catalog regenerate

---

## Task 26: HelloWorld.rs + Posao.hr + Jobweb Kenya

**Acceptance criteria:**
- [x] `helloworld_rs` free Serbian IT RSS ACTIVE
- [x] `posao_hr` free Croatian RSS ACTIVE
- [x] `jobweb_kenya` free Kenya RSS ACTIVE (first Africa)

**Verification:**
- [x] pytest + catalog regenerate

---

## Task 27: Demand Compass (docs → implement)

**Docs (done — revised against confirmation-bias):**
- [x] Idea [docs/ideas/freelance-demand-compass.md](../docs/ideas/freelance-demand-compass.md)
- [x] Discovery seed [data/research/discovery_watchlist.json](../data/research/discovery_watchlist.json)
- [x] [SPEC-research-intents.md](../docs/specs/SPEC-research-intents.md) (discovery + focus + lenses + LLM briefs)
- [x] [ADR-007](../docs/decisions/ADR-007-query-first-sync.md) revised
- [x] [plan](../docs/superpowers/plans/2026-10-20-query-first-daily-sync.md) revised
- [x] PRODUCT / CAPABILITY_MAP / ROADMAP / related SPECs / README / superseded query-only idea
- [x] Tech review [docs/reviews/2026-10-20-demand-compass-tech-review.md](../docs/reviews/2026-10-20-demand-compass-tech-review.md) → SPEC/ADR/plan corrections
- [x] Task 9 docs alignment (shipped vs remaining; no query-only / java-default product claims)

**Implementation acceptance:**
- [x] Registry `collection_mode` on every collector
- [x] `SearchQuery.kind` + migrate seed focus; seed discovery watchlist
- [x] **`job_intent_matches` M2M**; ingest upserts matches on crawl
- [x] Daily crawlers: dump → budgeted discovery/focus; idempotent UTC day; cron documented
- [x] Search-mode: no silent `*_DEFAULT_QUERY` / java-default product path; query simplify per API
- [x] Analytics `lens` via matches (dual-match + focus-only cases)
- [x] API + UI: Market scan, My focus, Sync now; accept watches (`POST /research/watches/accept`)
- [x] Explorer DB-first + explicit Refresh (`frontend/components/explorer/ExplorerRefresh.tsx`)
- [x] LLM brief handlers + MCP `render_demand_brief` (wrap trends where possible)
- [x] Assistant UI: brief-type chips + accept-watch (`BriefPanel` + `SuggestWatchesList` on `/assistant`)
- [x] `.env.example`: topic defaults deprecated; sync budgets; discovery watchlist pointer

**Verification:**
- [x] pytest coverage: `test_collection_mode`, `test_daily_crawlers`, `test_analytics_lenses`, `test_briefs`, `test_mcp_briefs`
- [x] Manual ops walkthrough: market rising/cooling → add focus → compare → accept LLM watch — [docs/ops/demand-compass-walkthrough.md](../docs/ops/demand-compass-walkthrough.md); `COMPASS_ACCEPT_WATCH=1 ./backend/scripts/smoke_compass.sh`

**Plan:** [docs/superpowers/plans/2026-10-20-query-first-daily-sync.md](../docs/superpowers/plans/2026-10-20-query-first-daily-sync.md)

---

## Task 28: i18n IT/EN + visual Demand Compass dashboards (docs → implement)

**Docs (done):**
- [x] Idea [docs/ideas/demand-compass-experience.md](../docs/ideas/demand-compass-experience.md)
- [x] [SPEC-i18n.md](../docs/specs/SPEC-i18n.md)
- [x] [SPEC-dashboard.md](../docs/specs/SPEC-dashboard.md) visual + chart inventory
- [x] [plan](../docs/superpowers/plans/2026-10-20-i18n-and-visual-dashboard.md)
- [x] PRODUCT / ROADMAP / CAPABILITY_MAP / ADR-004 / README updated

**Implementation acceptance:**
- [x] Design tokens (`--signal`, `--rise`, `--cool`) + chrome polish
- [x] `next-intl` + `en`/`it` catalogs; locale in prefs; `html lang`
- [x] Translate MVP surfaces (nav, Executive, Trends, Explorer, Assistant, charts chrome)
- [x] ECharts wrappers: RiseCool, Sparkline, GeoStrip, CompareDual (dynamic import)
- [x] Executive first viewport composition (hero chart + CTAs)
- [x] Assistant propose/briefs pass `locale` (`meta.locale` + `meta.narrative_locale=en` MVP)
- [x] Empty/thin-sample states localized; reduced-motion respected (chartTheme)
- [x] Formal SPEC-i18n / SPEC-dashboard acceptance checklists signed off (2026-10-20)

**Verification:**
- [x] Message key parity en ↔ it (294/294 keys, 2026-10-20 check)
- [ ] `npm run build` re-confirmed after latest UI polish (prior builds exist under `frontend/.next`) — **non-blocking** for MVP close
- [ ] Manual IT/EN toggle + hero chart from real trends API (ops sign-off) — **non-blocking**

**ROADMAP:** Next #1 (i18n polish) → **Now** (closed 2026-10-20). Task 28 MVP acceptance complete; open Verification items above are ops polish only.

**Plan:** [docs/superpowers/plans/2026-10-20-i18n-and-visual-dashboard.md](../docs/superpowers/plans/2026-10-20-i18n-and-visual-dashboard.md)

---

## Task 29: IT / CH / LU source gap — research + inclusion plan

**Research (done 2026-10-22):** parallel agents + live probes → [IT_CH_LU_COVERAGE.md](../docs/sources/IT_CH_LU_COVERAGE.md)

**Key findings (do not implement against these without legal gates):**
- IT: InfoJobs.it **closed**; no national PES vacancy API; P0 = ATS seeds + Excelsior/Eurostat open data
- CH: JobUp public API **ToS/robots conflict**; P0 = JobCloud affiliate + Adzuna/Careerjet licence + ATS; Job-Room needs SECO consent
- LU: P0 = ADEM CC0 open data + ATS `country=lu`; EURES only after ADEM NCO partnership

**Implementation plan:** [2026-10-22-it-ch-lu-sources.md](../docs/superpowers/plans/2026-10-22-it-ch-lu-sources.md)

**Acceptance (plan phase):**
- [x] Inventory existing IT/CH/LU collectors + catalog
- [x] Deep research IT / CH / LU (N agents)
- [x] Prioritized inclusion plan written (T0–T5)

**Implementation (2026-10-22):**
- [x] T0: InfoJobs geo `IT`→`ES`; catalog notes InfoJobs.it closed; JobUp/jobs.ch ToS flags
- [x] T1: ATS seeds — Ashby `satispay`, Lever `musixmatch`, Workable `moneyfarm`, SR `Talan`/`Devoteam`, Workday Swisscom; COLLECTOR_GEO ATS affinity
- [x] T2: Eurostat `isoc_sk_oja` / `oja2` allowlisted (ADEM script already exists)
- [x] T3: Adzuna `COLLECTOR_GEO` + default `ADZUNA_COUNTRIES` include `it`,`ch`
- [ ] Partner emails (JobCloud / SECO / Adzuna licence) — ops, not code
- [x] Live compose corpus check (2026-10-22): jobs with `country_code` IT=169, CH=677, LU=23 (ATS/geo seeds already inserting)

**Verification:**
- [x] Coverage doc + plan linked from this task
- [x] `pytest tests/test_it_ch_lu_geo.py` (+ eurostat/infojobs/credentialed) pass
- [x] Local stack: IT/CH/LU inventory present; catalog ACTIVE only for authorized paths (partner boards remain NEEDS_CREDENTIALS/REJECTED)

---

## Task 30: Complete chart dashboard (KPI cockpit)

**Docs (draft — approve before code):**
- [x] [SPEC-dashboard-charts.md](../docs/specs/SPEC-dashboard-charts.md) — full KPI catalog + chart inventory + languages + world map
- [x] [plan](../docs/superpowers/plans/2026-10-22-complete-chart-dashboard.md) — Tasks 1–7 (P0→P2)

**P0 implementation (shipped 2026-10-22):**
- [x] Facets API + remote/contract donuts
- [x] Language extraction + backfill → `language_requirements`
- [x] Languages analytics + `/languages` + Executive lang rank
- [x] World choropleth on Countries
- [x] Rates box + tech rank bars + source mix

**P1/P2:** co-occurrence / seniority / lang×country heats shipped on `/relations` (waves 0–5); combo chips + profile language match KPI still open.

**Gate:** SPEC-dashboard-charts + SPEC-correlative-relations accepted; coding landed.
