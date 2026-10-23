# Roadmap

Aligned with [PRODUCT.md](PRODUCT.md) and [CAPABILITY_MAP.md](CAPABILITY_MAP.md).

## Now (shipped or docs-complete)

### Global sources

- Catalog ~193 entries (categories A–I), duplicates corrected, statuses in [`data/sources/catalog.json`](../data/sources/catalog.json).
- Docs: [sources/VALIDATION_REPORT.md](sources/VALIDATION_REPORT.md), [sources/COVERAGE_GAPS.md](sources/COVERAGE_GAPS.md), [SPEC-sources.md](specs/SPEC-sources.md).
- Schema/seed sync for catalog + verification fields; Sources UI + catalog/FX APIs.
- ACTIVE job connectors: Remotive, Arbeitnow, Remote OK, Working Nomads, We Work Remotely, The Muse, Jobicy, Himalayas, HN Who is hiring, DevITJobs, NoFluffJobs, Reed (RSS), Get on Board, MyCareersFuture, JobUp, NAV Arbeidsplassen, Landing.jobs, okemprego (PT), Canada Job Bank open data, Kalibrr, DOU.ua, Authentic Jobs, Wantedly, Duunitori, Jobindex, Wanted, Instahyre, Hasjob, HelloWorld.rs, Posao.hr, Jobweb Kenya, Dev Global Jobs (LU/BG), ViewJobs (AU), Greenhouse/Lever/Ashby/SmartRecruiters (configured), Arbetsförmedlingen JobSearch, CSV/JSON/XLSX import.
- **Eurostat stats helper:** `GET /api/v1/stats/eurostat/series` (allowlisted datasets; reference only) + Rates page panel.
- **ATS tenant expand:** Greenhouse 28 / Lever 2 / Ashby 9 probed-green defaults; collectors cap 40 jobs/tenant.
- Sources UI: **Run all free public** (skips paid credential scaffolds).
- Prefer free public APIs/RSS over paid aggregators ([ADR-003](decisions/ADR-003-authorized-connectors-only.md)); credentialed scaffolds remain optional.
- **Taxonomy lookup:** ESCO + JobTech (`/api/v1/taxonomy/{esco,jobtech}/search`) on Skills page (free public APIs; reference labels only).
- FX helpers: Frankfurter, ECB.

### Core product

- Classify: rules / hybrid / llm, taxonomy, rate NULL semantics.
- Analytics: summary, rates, countries, co-occurrence, trends, quality.
- **Relations cockpit (`/relations`):** sticky PeriodChip; heatmaps (tech×tech, tech×country, lang×country, role×tech, seniority×tech) + temporal series (tech, country, rate medians); tabs Heatmaps/Series with `?view=`; APIs under `/api/v1/market/matrix/*` and `/series/*` ([SPEC-correlative-relations.md](specs/SPEC-correlative-relations.md)).
- Dashboard pages (guided presentation) including Sources.
- Profile, applications, alerts, weekly JSON report.
- Ops: optional API key, in-memory rate limit, optional scheduler, CI, smoke, PRODUCTION notes.
- Documentation suite: PRODUCT, SPEC*, ADRs, customization + trends-only requirements.
- **MCP analytics (stdio):** `python -m app.mcp` — metadata, semantic catalog, allowlisted SQL, propose/validate DashboardSpec & ReportSpec, materialize_report ([docs/mcp/CURSOR.md](mcp/CURSOR.md)).
- **Dashboard customization:** Guided | Trends-only toggle, Prefs panel (period, focus, nav hide, presets), Executive/Trends respect `view_mode`.
- **In-app Assistant:** `/assistant` + `POST /api/v1/assistant/propose` → Apply DashboardSpec to prefs.
- **Production hardening:** `scheduler_tick.sh`, `RATE_LIMIT_BACKEND=redis|memory`, `GET /api/v1/ops/metrics`, `/livez` liveness + `/readyz`/`/healthz` readiness (503 if DB down; Compose healthcheck `/readyz`), `SecurityHeadersMiddleware`, non-root images (`appuser`/`node` uid 1000), prod CORS reject empty/`*`, `COMPASS_SMOKE` in `compose_stack_relaunch.sh`, Sources catalog browser filters.
- **Gold-label eval:** `data/eval/gold_labels.json` + `GET|POST /api/v1/llm/evaluation/gold` + Quality UI.
- **Prefs sync:** `GET|PUT /api/v1/profile/dashboard-prefs` (Alembic 0003); PrefsPanel Load/Save; localStorage remains primary.
- **Credentialed scaffolds:** Adzuna, USAJOBS, France Travail, Bundesagentur, Jooble — env keys; catalog stays `NEEDS_CREDENTIALS` until live run; `promote_source_active.py` gates DB ACTIVE on insert evidence. Optional OXR FX overlay. Reed is free via RSS.
- **Ops restore path:** `restore_smoke.sh` + `psql_cmd.sh` (schema → temp DB); expanded probed ATS defaults (Greenhouse/Lever/Ashby).

### Demand Compass (shipped)

- **Research intents:** `SearchQuery.kind` (discovery/focus), seed from [`data/research/discovery_watchlist.json`](../data/research/discovery_watchlist.json), `job_intent_matches` M2M, no silent `*_DEFAULT_QUERY` on product collect path.
- **Daily crawlers:** budgeted dump → discovery → focus; UTC-day idempotency; cron via `scheduler_tick.sh` ([PRODUCTION.md](PRODUCTION.md)). Local single-replica Compose: `ENABLE_SCHEDULER=true` + `SCHEDULER_INTERVAL_SECONDS=86400` in `.env` (tick on boot, then daily).
- **Lenses:** analytics `lens=market|focus|compare` via `job_intent_matches`; UI `LensToggle` on Executive, Trends, Jobs, Skills, Quality (plus Rates/Countries/Assistant).
- **Market-scan / focus UI:** `/market-scan`, `/focus`, Sync now per intent, discovery coverage warn; Explorer DB-first + explicit Refresh (`ExplorerRefresh`).
- **Assistant briefs UI:** `/assistant` `DemandCompassSection` chips (`rising_cooling`, `where_demand`, `adjacent`, `focus_vs_market`, `suggest_watches`) + accept-watch via `WatchCandidates` → `POST /research/watches/accept`.
- **MCP:** `render_demand_brief` (same brief types; `suggest_watches` never INSERTs).
- **Ops walkthrough:** [ops/demand-compass-walkthrough.md](ops/demand-compass-walkthrough.md) (market → focus → compare → accept LLM watch); automatable via `backend/scripts/smoke_compass.sh` (+ optional `COMPASS_ACCEPT_WATCH=1`); CI job `compass-smoke`.
- **Evidence tier:** `Job.evidence_tier` `standard`|`thin` (Alembic `0007`); capped/snapshot connectors (ViewJobs, Job Bank CA, …) ingest as **thin** ([ADR-001](decisions/ADR-001-evidence-first-kpis.md)).
- **Soft-expire:** closed listings → `closed_stale` after 45d; excluded from `base_job_query` used by skills/rates/trends KPI denominators.
- **Min evidence gate:** default `min_evidence=standard` on skills co-occurrence, rates, technology trends, and briefs (`lens_sample_size`); thin rows remain in DB and Quality inventory.
- **Coverage + quality:** `coverage_notes` on dashboard **summary** and **countries**; Quality **by_source** includes `pct_thin`.
- **Run telemetry:** `CollectionRun.summary` (Alembic `0009`); analytics indexes (`0008`).
- **Intent country suggest:** `IntentCountriesSuggest` — suggests Focus chrome Country filter only; never auto-applies.
- **GEO smoke:** `backend/scripts/smoke_geo_country.sh` (optional `GEO_SMOKE=1` on `smoke_e2e.sh`); no Indeed/LinkedIn scrape ([ADR-003](decisions/ADR-003-authorized-connectors-only.md)).
- Docs/plan: [SPEC-research-intents.md](specs/SPEC-research-intents.md), [ADR-007](decisions/ADR-007-query-first-sync.md), [plan](superpowers/plans/2026-10-20-query-first-daily-sync.md).

### i18n + visual dashboards (i18n MVP accepted 2026-10-20)

- **`next-intl`:** `app/[locale]/…`, `messages/en.json` + `it.json` (294-key parity), locale in prefs + chrome toggle, `html lang`.
- **Assistant locale:** propose/briefs accept `locale` `en`|`it`; `meta.locale` echoed; **`meta.narrative_locale=en` MVP** (no Italian narrative generation). `ProposeSection` + `DemandCompassSection` pass `useLocale()`.
- **Signal-desk charts:** ECharts wrappers `RiseCoolChart`, `GeoStrip`, `CompareDual`, `Sparkline` (dynamic import); Executive jobs/day from `summary.jobs_per_day`; design tokens (`--signal`, `--rise`, `--cool`).
- **SPEC-i18n** Accepted (MVP). **SPEC-dashboard** Demand Compass / Explorer / i18n + jobs/day sparkline (`summary.jobs_per_day`) — [SPEC-i18n.md](specs/SPEC-i18n.md) · [SPEC-dashboard.md](specs/SPEC-dashboard.md) · [plan](superpowers/plans/2026-10-20-i18n-and-visual-dashboard.md).
- *(Former Next #1 “i18n polish” closed: locale pass-through + SPEC-i18n sign-off.)*

## Next (implement from tasks/todo.md)

1. Live keyed runs for credentialed scaffolds → flip catalog `ACTIVE` with evidence. **Blocked (2026-10-20):** Adzuna / USAJOBS / France Travail / Bundesagentur / Jooble env keys empty (`credentials_present=false`); zero insert-evidence `CollectionRun`s — no honest ACTIVE flips. Public set already ACTIVE; DB insert evidence so far: `remotive` + `remoteok` only ([VALIDATION_REPORT.md](sources/VALIDATION_REPORT.md)).
2. Authorized marketplace exports / ATS expansion when partnerships allow.
3. Optional: confirm Cursor MCP loads from `.cursor/mcp.json` — operator checklist in [mcp/CURSOR.md](mcp/CURSOR.md) (copy example → absolute paths → restart → Settings→MCP green `fmi-analytics` → `build_mcp()` smoke). **Progress (2026-10-21):** gitignored `.cursor/mcp.json` present with absolute venv paths; `build_mcp()` smoke OK (**11** tools). Cursor Settings → MCP green status **not confirmed in this session** (UI not visible from agent).

*(Former Next “Executive jobs/day sparkline” closed: `GET /dashboard/summary` → `jobs_per_day` → `SparklineLazy`.)*

Plans:

- [superpowers/plans/2026-10-20-query-first-daily-sync.md](superpowers/plans/2026-10-20-query-first-daily-sync.md)
- [superpowers/plans/2026-10-20-i18n-and-visual-dashboard.md](superpowers/plans/2026-10-20-i18n-and-visual-dashboard.md)
- [superpowers/plans/2026-10-20-dashboard-customization.md](superpowers/plans/2026-10-20-dashboard-customization.md)
- [superpowers/plans/2026-10-20-production-hardening.md](superpowers/plans/2026-10-20-production-hardening.md)
- [superpowers/plans/2026-10-20-global-sources.md](superpowers/plans/2026-10-20-global-sources.md)
- [superpowers/plans/2026-10-20-mcp-schema-dashboards.md](superpowers/plans/2026-10-20-mcp-schema-dashboards.md)

## Later (persona-aligned, not claimed shipped)

- Italian (locale-aware) assistant / evidence narrative generation (`meta.narrative_locale` beyond fixed `en` MVP).
- Dedicated ECharts `remote_mix` / `rates_box` / `cooccur_heat` wrappers (Countries/Rates/Skills still table/card OK).
- Broader marketplace / board APIs: LinkedIn, Malt, Indeed, Upwork, Careerjet, StepStone, etc. (credentials/partnerships).
- Stats-ingest: Eurostat, BLS, O*NET, national open data (comparability rules).
- Salary survey / guide import paths (PDF/manual where license allows).
- Procurement module: TED, Contracts Finder, SAM.gov, etc. (distinct from jobs).
- Taxonomies: ESCO / O*NET sync beyond reference links.
- RAG knowledge layer over job descriptions / imported docs (complements MCP; does not replace it).
- PDF weekly reports.
- OAuth2/OIDC multi-user.
- Kubernetes / multi-region deploy.
- Optional Java/Spring sidecar for enterprise integration demos (not required for FMI core).

Plan stub: [superpowers/plans/2026-10-20-rag-knowledge-layer.md](superpowers/plans/2026-10-20-rag-knowledge-layer.md)
