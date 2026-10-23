# Source validation report (2026-10-20)

Non-destructive HTTP probes and public documentation review for the global sources program (categories A–I; see [README.md](README.md)). **ACTIVE** means a connector in this repo returned real records. Credentials were not fabricated. Procedure and statuses: [../specs/SPEC-sources.md](../specs/SPEC-sources.md).

## Summary

See live counts via `GET /api/v1/sources/catalog/summary` or regenerate:

```bash
python3 backend/scripts/generate_source_catalog.py
```

Catalog file: [`data/sources/catalog.json`](../../data/sources/catalog.json)

| Status | Meaning |
|--------|---------|
| ACTIVE | Connector implemented + live data verified |
| VALIDATED | Access pattern verified; not (yet) a full job ingest path |
| NEEDS_CREDENTIALS | Official API/partner path needs keys/agreements |
| UNDER_REVIEW | Docs incomplete or open-data path not wired |
| REJECTED | Not a suitable automated job source for FMI |
| DISCOVERED | Duplicate or pointer entry |
| BLOCKED / DEGRADED / DEPRECATED | Reserved for runtime ops |

## Connectors marked ACTIVE (implemented)

| Source | Key | Evidence |
|--------|-----|----------|
| Remotive | `remotive` | GET `/api/remote-jobs` 200 |
| Arbeitnow | `arbeitnow` | GET job-board API 200 |
| Remote OK | `remoteok` | GET `/api` 200 (attribution required) |
| Working Nomads | `working_nomads` | GET `/api/exposed_jobs/` 200 |
| We Work Remotely | `weworkremotely` | RSS programming jobs 200 |
| The Muse | `themuse` | Public jobs API 200 |
| Jobicy | `jobicy` | Free `GET /api/v2/remote-jobs` 200 (attribution) |
| Himalayas | `himalayas` | Free `GET /jobs/api` 200; `pubDate` is Unix epoch (collector fixed 2026-10-20; re-run succeeded, 0 date errors) |
| HN Who is hiring | `hn_whoishiring` | Algolia public search 200 (hiring comments) |
| Greenhouse boards | `greenhouse` | Per-board API; defaults 29 tenants (HTTP 200 + payload; +`lyft` 180 jobs 2026-10-21); empty → non-runnable |
| Lever postings | `lever` | Per-site API; defaults `spotify`,`palantir`,`wealthfront` (wealthfront 23 jobs 2026-10-21) |
| Ashby boards | `ashby` | ACTIVE with default `ASHBY_ORGS` (10 orgs incl. granola,runway,supabase); empty → non-runnable |
| SmartRecruiters | `smartrecruiters` | Public company postings (endava/ServiceNow/DeliveryHero/Wise/Allegro/Uber) |
| Personio boards | `personio` | Public `search.json` per slug; defaults 8 DACH tech tenants (HTTP 200 + non-empty array; probed 2026-10-21); empty → non-runnable |
| Arbetsförmedlingen | `arbetsformedlingen` | JobTech JobSearch `GET /search` 200 (public, no key) |
| ESCO API | _(taxonomy)_ | Free `GET /api/v1/taxonomy/esco/search` — reference labels only |
| JobTech Taxonomy API | _(taxonomy)_ | Free `GET /api/v1/taxonomy/jobtech/search` — Swedish labels only |
| DevITJobs | `devitjobs` | Free `GET /api/jobsLight` on uk/com hosts 200 |
| NoFluffJobs | `nofluffjobs` | Free `GET /api/posting` 200 (large dump; connector caps) |
| Reed | `reed` | Free public RSS `GET /jobs/rss?keywords=` 200 (ACTIVE path); optional `REED_API_KEY` JSON enrichment only |
| Get on Board | `getonbrd` | Free LATAM `GET /api/v0/search/jobs` 200 |
| MyCareersFuture | `mycareersfuture` | Free SG gov `GET /v2/jobs?search=` 200 |
| JobUp | `jobup` | Free Swiss `GET /api/v1/public/search`; API caps **`rows` ≤ 20** (`ROWS_PER_PAGE=20`). Prior 422 was `rows=50`, not egress. Live insert evidence: run 104+ |
| NAV Arbeidsplassen | `nav_arbeidsplassen` | Free NO PES `GET /stillinger/api/search` 200 |
| Landing.jobs | `landing_jobs` | Free EU tech `GET /api/v1/jobs` 200 (EUR salaries) |
| Kalibrr | `kalibrr` | Free SEA `GET /api/job_board/search` 200 |
| DOU.ua | `dou_ua` | Free UA IT `GET /vacancies/feeds/?category=` RSS 200 |
| Authentic Jobs | `authentic_jobs` | Free FeedBurner jobs RSS 200 (site `/rss` editorial) |
| Wantedly | `wantedly` | Free JP `GET /api/v1/projects` 200 |
| Duunitori | `duunitori` | Free FI `GET /api/v1/jobentries` 200 |
| Jobindex | `jobindex` | Free DK `GET /jobsoegning.rss?q=` 200 |
| Wanted | `wanted` | Free KR `GET /api/v4/jobs` 200 |
| Instahyre | `instahyre` | Free IN `GET /api/v1/job_search/` 200 |
| Hasjob | `hasjob` | Free IN `GET /?format=json` 200 |
| HelloWorld.rs | `helloworld_rs` | Free RS IT `GET /rss` 200 |
| Posao.hr | `posao_hr` | Free HR `GET /rss` 200 |
| Jobweb Kenya | `jobweb_kenya` | Free KE `GET /feed/` RSS 200 |
| Tecnoempleo | `tecnoempleo` | Free ES IT RSS; live ingest **80** inserts (source_id 57, run 35, 2026-10-21); catalog ACTIVE id 24 |
| Le Forem (ODWB) | `le_forem` | Free Wallonia ODWB dump; live ingest **180** inserts (source_id 68, run 37, 2026-10-21); catalog ACTIVE id 35 |
| MPSV / Úřad práce | `mpsv` | CZ open-data JSON-LD stream; live ingest **289** inserts (source_id 306, run 39, 2026-10-21); catalog ACTIVE id 195 |
| findmethatdamjob.nl | `findmethatdamjob` | Free documented `GET https://gigsignal-api.fly.dev/api/jobs?location=amsterdam` 200 (~1280 NL listings, 2026-10-21); not UWV PES — catalog ACTIVE id 197 |
| Dev Global Jobs | `devglobaljobs` | Free display API (LU/BG); live insert **15** (run 222); request ISO2 tags `country_code`; catalog ACTIVE id 198 |
| ViewJobs | `viewjobs` | Free AU MCP `search_jobs`; live insert **37** (run 223); thin evidence; catalog ACTIVE id 199 |
| OkEmprego | `okemprego` | Free PT IT API; live insert **148** (run 225); all `country_code=PT`; catalog ACTIVE id 200 |
| Canada Job Bank | `jobbank_ca` | ESDC open-data CSV (OGL); live insert **179** (run 228); thin/snapshot; catalog ACTIVE id 201 |
| Eurostat | _(stats)_ | Free `GET /api/v1/stats/eurostat/series` — official stats reference only |
| Frankfurter | `frankfurter` | FX helper `/api/v1/fx/rates` |
| ECB Data API | `ecb_fx` | FX helper fallback |
| Manual import | `manual_import` | CSV/JSON/XLSX upload |

## Newly registered collectors (2026-10-21)

| Key | Catalog / DB | Notes |
|-----|--------------|-------|
| `tecnoempleo` | ACTIVE | Live insert evidence below. |
| `le_forem` | ACTIVE | Live insert evidence below. |
| `mpsv` | ACTIVE | Compact JSON 404 → `volna-mista.jsonld`; live insert evidence below. |
| `findmethatdamjob` | ACTIVE | NL public API; live insert run **124** received 63 inserted **63**; re-run **126** = 63 updates (upsert). |
| `findwork` | NEEDS_CREDENTIALS (scaffold) | Fail-closed. Keys: `FINDWORK_API_KEY` (+ optional `FINDWORK_LOCATION`). **No live insert** until operator run + promote. |
| `careerjet` | NEEDS_CREDENTIALS (scaffold) | Fail-closed. `CAREERJET_API_KEY` + `CAREERJET_USER_IP` (Basic v4 query); optional `CAREERJET_LOCALES` (default IT/DE/CH/LU). Publisher account required. **No live insert** until operator run + promote. |
| `infojobs` | NEEDS_CREDENTIALS (scaffold) | Fail-closed. `INFOJOBS_CLIENT_ID` + `INFOJOBS_CLIENT_SECRET` (HTTP Basic). Partner agreement may apply for bulk reuse. **No live insert** until operator run + promote. |

Related keyed env (scaffolds unchanged; still not ACTIVE without live promote): Adzuna multi-country via `ADZUNA_COUNTRIES` / `ADZUNA_COUNTRY`; USAJOBS optional `USAJOBS_JOB_CATEGORY_CODE` (e.g. `2210`).

### Live ingest (2026-10-21) — tecnoempleo / le_forem / mpsv

Operator `POST /api/v1/sources/{id}/run` (local compose). All three remain **ACTIVE** (promote + catalog aligned).

| Key | source_id | run_id | status | received | inserted | updated |
|-----|-----------|--------|--------|----------|----------|---------|
| `tecnoempleo` | 57 | 35 | succeeded | 80 | **80** | 0 |
| `le_forem` | 68 | 37 | succeeded | 200 | **180** | 0 |
| `mpsv` | 306 | 39 | succeeded | 300 | **289** | 0 |

**DB confirmation (2026-10-21, local compose):** same counts re-read from Postgres via `docker compose exec -T api python` → `app.storage.db.SessionLocal` + `sqlalchemy.text` on `collection_runs` joined to `sources` on `source_id` (filter `sources.connector_type`; there is no `sources.key` column). All three sources remain `verification_status=ACTIVE`, `enabled=true`.

Later re-runs on this DB (upsert/dedup; not used as first promote evidence): `le_forem` runs 54/79 and `mpsv` runs 56/81 → **0** inserted with full `records_updated` (180 / 289); `tecnoempleo` run 88 → 58 inserted / 22 updated. After jobs exist, expect many runs to show **`records_inserted=0`** with non-zero **`records_updated`** — normal canonical-url upsert, not a failed fetch.

**JobUp** (`jobup`, source_id 201): earlier runs 44/46/70 → **partial** because collector requested `rows=50` while public API returns **422** above **20**. Fixed `ROWS_PER_PAGE=20`. Operator run **104** `succeeded` received **60** inserted **57**; follow-up `kubernetes` run inserted **47**. Catalog **ACTIVE**.

## Needs credentials (selected)

Credentialed scaffolds (fail closed; ACTIVE only after live): Adzuna, USAJOBS, France Travail, Bundesagentur, Jooble, Findwork, **Careerjet**, **InfoJobs** (collectors in `COLLECTORS`; catalog `NEEDS_CREDENTIALS` until live promote). Also Indeed, LinkedIn, StepStone, Upwork, Malt, Freelancer, O*NET, and others with `NEEDS_CREDENTIALS` but no registry connector yet. Keys enable the collector but **do not** set ACTIVE until a live run persists jobs (`promote_source_active.py`). Adzuna: `ADZUNA_APP_ID`/`ADZUNA_APP_KEY` + optional multi-country `ADZUNA_COUNTRIES` (fallback `ADZUNA_COUNTRY`). USAJOBS: `USAJOBS_API_KEY`/`USAJOBS_USER_AGENT` + optional `USAJOBS_JOB_CATEGORY_CODE`. Findwork: `FINDWORK_API_KEY` (+ optional `FINDWORK_LOCATION`). Careerjet: `CAREERJET_API_KEY`/`CAREERJET_USER_IP` (+ optional `CAREERJET_LOCALES`). InfoJobs: `INFOJOBS_CLIENT_ID`/`INFOJOBS_CLIENT_SECRET` (+ optional `INFOJOBS_COUNTRY`). Reed is free via public RSS (optional API key for richer JSON). France Travail may require Emploi Store subscription. Bundesagentur Jobsuche v6 returned records in a keyed local probe — still not catalog ACTIVE until operator ingest. Open Exchange Rates: optional FX overlay env only (not a job connector).

### Audit 2026-10-20 (no secrets; presence-only)

Local `.env` / compose API env had **no** values for `ADZUNA_APP_ID`/`ADZUNA_APP_KEY`, `USAJOBS_API_KEY`, `FRANCE_TRAVAIL_CLIENT_ID`/`FRANCE_TRAVAIL_CLIENT_SECRET`, `BUNDESAGENTUR_API_KEY`, `JOOBLE_API_KEY` (keys absent/empty; `credentials_present=false` via `GET /api/v1/ops/connectors`). DB check: all five scaffolds remain `NEEDS_CREDENTIALS`, `enabled=false`, **zero** `CollectionRun` rows with `records_inserted > 0`. Fail-closed collect probes (query=`python`): each returned `records=0` with a required-credentials error class (no network auth success). **No catalog ACTIVE flips** this pass — operators must set keys, run ingest, then `promote_source_active.py` + regenerate catalog.

### Public re-probe 2026-10-20 (API container; counts only)

Reconfirmed already-ACTIVE free connectors via in-process `collect()` (no secret headers logged): remotive 10, remoteok 99, arbeitnow 300, jobicy 50, himalayas 40, reed RSS 25, devitjobs 160, hn_whoishiring 178, working_nomads 44, weworkremotely 25, themuse 20, authentic_jobs 21, arbetsformedlingen 100, greenhouse 887, landing_jobs 50, nav_arbeidsplassen 25 — **16/16 OK**. No non-ACTIVE public registry connector remains to flip; remaining keyed scaffolds blocked solely by missing operator credentials.

### DB CollectionRun insert evidence (2026-10-20, local compose)

Persisted `collection_runs` with `status=succeeded` and `records_inserted > 0` (jobs table matches):

| Key | verification_status | ok_insert_runs | sum_inserted |
|-----|---------------------|----------------|--------------|
| `remotive` | ACTIVE (confirmed) | 1 | 10 |
| `remoteok` | ACTIVE (confirmed) | 1 | 99 |

All other public registry connectors (`arbeitnow`, `reed`, ATS boards, Jobicy/Himalayas/HN, regional free APIs/RSS, etc.) remain **catalog + DB `ACTIVE` / `enabled`** from prior HTTP/`collect()` evidence; they have **zero** insert-evidence `CollectionRun` rows in this DB snapshot (not demoted — not yet ingested via operator run). Credentialed scaffolds unchanged: still `NEEDS_CREDENTIALS`, `enabled=false`, zero inserts. **Catalog flips this pass: none** (already correctly labeled).

### DB CollectionRun insert evidence expand (2026-10-20 → 2026-10-21, local compose)

Goal: expand honest insert evidence beyond `remotive` + `remoteok` for **public ACTIVE** collectors (no credentials). Keyed scaffolds not flipped.

**Gap before this pass (ACTIVE + enabled + registry collector + not scaffold + zero insert-evidence runs):** 32 connectors, including `working_nomads`, `jobicy`, `himalayas`, `arbeitnow`, `weworkremotely`, `reed`, ATS boards, regional free APIs/RSS, etc.

**Operator runs this pass** (sequential `POST /api/v1/sources/{id}/run?query=python` with ~12s pauses; plus one limited in-container jobicy CollectionRun after tag fix). Counts are per-run `records_inserted` (not cumulative):

| When (UTC) | Key | Run id | status | received | inserted | notes |
|------------|-----|--------|--------|----------|----------|-------|
| 2026-10-20T22:13:55Z | `working_nomads` | 3 | succeeded | 14 | **14** | query filter `python` |
| 2026-10-20T22:14:09Z | `jobicy` | 4 | succeeded | 50 | 0 | ingest errors — nested list tags (fixed below) |
| 2026-10-20T22:14:24Z | `himalayas` | 5 | partial | 6 | **6** | query filter; collector `pubDate` warnings |
| 2026-10-20T22:16:16Z | `arbeitnow` | 7 | succeeded | 3 | **3** | query filter `python` |
| 2026-10-20T22:19:43Z | `jobicy` | 26 | succeeded | 25 | **25** | after tag flatten; batch capped at 25 |

Also observed on the same DB shortly after (other concurrent local ops / retries; still public no-key): `reed` run 14 inserted 25; `weworkremotely` run 16 inserted 24; additional `jobicy`/`himalayas`/`remoteok` insert runs. Not used to flip catalog status.

**Jobicy fix (required for insert evidence):** `jobIndustry` / `jobType` arrive as lists; nested tags broke `classify_job` (`TypeError`). Collector now flattens to `list[str]` and string `job_type` (`backend/app/collectors/jobicy.py`).

**Cumulative insert-evidence snapshot** (`status in (succeeded, partial)` and `records_inserted > 0`):

| Key | verification_status | ok_insert_runs | sum_inserted | last_insert_at (UTC) |
|-----|---------------------|----------------|--------------|----------------------|
| `arbeitnow` | ACTIVE | 1 | 3 | 2026-10-20T22:16:16Z |
| `himalayas` | ACTIVE | 2 | 40 | 2026-10-20T22:19:22Z |
| `jobicy` | ACTIVE | 3 | 165 | 2026-10-20T22:19:43Z |
| `reed` | ACTIVE | 1 | 25 | 2026-10-20T22:17:12Z |
| `remoteok` | ACTIVE | 2 | 187 | 2026-10-20T22:17:05Z |
| `remotive` | ACTIVE | 1 | 10 | 2026-10-20T17:53:39Z |
| `weworkremotely` | ACTIVE | 1 | 24 | 2026-10-20T22:18:35Z |
| `working_nomads` | ACTIVE | 1 | 14 | 2026-10-20T22:13:55Z |

Credentialed scaffolds unchanged: `adzuna`, `usajobs`, `france_travail`, `bundesagentur`, `jooble` still `NEEDS_CREDENTIALS`, `enabled=false`, zero insert-evidence runs. **Catalog ACTIVE flips this pass: none.**

### Free geo ACTIVE collectors — DB insert evidence (2026-10-21, local compose)

Public no-key dump/RSS connectors already **ACTIVE** in catalog + DB. Primary operator ingest rows (first successful persist for each):

| connector_type | source_id | run_id | status | received | inserted | updated |
|----------------|-----------|--------|--------|----------|----------|---------|
| `tecnoempleo` | 57 | 35 | succeeded | 80 | **80** | 0 |
| `le_forem` | 68 | 37 | succeeded | 200 | **180** | 0 |
| `mpsv` | 306 | 39 | succeeded | 300 | **289** | 0 |

**Cumulative insert-evidence addendum** (same DB; `status in (succeeded, partial)` and `records_inserted > 0`):

| connector_type | verification_status | ok_insert_runs | sum_inserted | last_insert_at (UTC) |
|----------------|---------------------|----------------|--------------|----------------------|
| `tecnoempleo` | ACTIVE | 2 | 138 | 2026-10-20T22:53:20Z |
| `le_forem` | ACTIVE | 1 | 180 | 2026-10-20T22:49:37Z |
| `mpsv` | ACTIVE | 1 | 289 | 2026-10-20T22:49:46Z |

Re-runs may add zero new inserts (see upsert note in **Live ingest (2026-10-21)** above). **JobUp** insert evidence: run **104** (57 inserts) after `rows≤20` fix.

### Operator verify + upsert/dedup (2026-10-21, local compose)

Goal: confirm public ACTIVE no-key collectors fetch via `POST /api/v1/sources/{id}/run?query=python` and that re-runs upsert instead of exploding `jobs` row counts. No keyed scaffolds touched; no catalog ACTIVE flips.

**Enabled ACTIVE sources in DB at start of this verify:** 35 rows (`verification_status=ACTIVE`, `enabled=true`), including preferred no-key keys below (ids): `remotive` 1, `arbeitnow` 2, `remoteok` 32, `working_nomads` 33, `weworkremotely` 34, `reed` 50, `jobicy` 193, `himalayas` 194.

**Primary runs this verify** (HTTP 200 unless noted; API restarted mid-pass once — arbeitnow first attempt connection reset, succeeded on retry as run 27):

| Key | source_id | run_id | status | received | inserted | updated | duplicates | errors | notes |
|-----|-----------|--------|--------|----------|----------|---------|------------|--------|-------|
| `remotive` | 1 | 9 | succeeded | 10 | 0 | 10 | 0 | 0 | prior rows present → all updates |
| `remoteok` | 32 | 10 | succeeded | 100 | 88 | 12 | 0 | 0 | net new inserts |
| `working_nomads` | 33 | 11 | succeeded | 14 | 0 | 14 | 0 | 0 | prior insert evidence |
| `jobicy` | 193 | 12 | succeeded | 50 | 0 | 0 | 0 | 50 | pre-fix tag ingest errors (see expand above) |
| `himalayas` | 194 | 13 | partial | 6 | 0 | 6 | 0 | 0 | collector `pubDate` warnings (6) |
| `reed` | 50 | 14 | succeeded | 25 | **25** | 0 | 0 | 0 | first RSS insert evidence |
| `arbeitnow` | 2 | 27 | succeeded | 4 | **1** | 3 | 0 | 0 | after API healthy |
| `weworkremotely` | 34 | 28 | succeeded | 7 | 0 | 7 | 0 | 0 | prior insert run 16 had 24 inserts |
| `jobicy` | 193 | 32 | succeeded | 100 | **75** | 25 | 0 | 0 | post tag-flatten; jobs table = 100 |

**Double-run dedup check (`reed`, source_id=50):**

| Step | jobs row count | run | received | inserted | updated |
|------|----------------|-----|----------|----------|---------|
| After first insert (run 14) | **25** | 14 | 25 | 25 | 0 |
| Re-run #1 | **25** | 29 | 25 | 0 | 25 |
| Re-run #2 | **25** | 30 | 25 | 0 | 25 |

Row count stayed 25; second/third runs were pure updates (no insert growth). Spot-check `remotive`: jobs stayed **10** across an extra re-run (10 received → 0 inserted / 10 updated).

**Jobs table after verify (selected keys):** remotive 10, remoteok 187, working_nomads 14, jobicy 100, himalayas 40, reed 25, arbeitnow 4, weworkremotely 24.

### ATS tenant expand (2026-10-21, public JSON only)

Honest curl probes (UA `FMI-MarketIntel/1.0`, no credentials). Added **only** green non-empty boards to Settings / `.env.example` defaults:

| Platform | Slug | HTTP | Bytes | Jobs in payload | Endpoint |
|----------|------|------|-------|-----------------|----------|
| Greenhouse | `lyft` | 200 | 140677 | 180 | `boards-api.greenhouse.io/v1/boards/lyft/jobs` |
| Lever | `wealthfront` | 200 | 439290 | 23 | `api.lever.co/v0/postings/wealthfront?mode=json` |
| Ashby | `supabase` | 200 | 761237 | 55 | `api.ashbyhq.com/posting-api/job-board/supabase` |

Not added (same session): many GH/Lever/Ashby slug guesses returned 404; SmartRecruiters identifier guesses returned HTTP 200 with empty `content` (e.g. Visa/Siemens/Zalando) — not treated as live boards. No new marketplace partnerships or ACTIVE catalog flips beyond existing ATS connectors.

**Personio public boards (2026-10-21, UA `FMI-MarketIntel/1.0`, `GET https://{slug}.jobs.personio.de/search.json` only):**

| Slug | HTTP | Bytes | Jobs | Notes |
|------|------|-------|------|-------|
| `1komma5grad` | 200 | 196896 | 304 | DE cleantech / energy |
| `chrono24` | 200 | 5541 | 17 | CH marketplace (watch platform) |
| `finanzguru` | 200 | 2330 | 4 | DE fintech |
| `tado` | 200 | 869 | 2 | DE smart-home / IoT |
| `kiwi` | 200 | 1281 | 3 | Travel tech (DACH) |
| `personio-gmbh` | 200 | 860 | 3 | DE HR tech (Personio) |
| `alcemy` | 200 | 1331 | 3 | DE cleantech / materials |
| `researchgate` | 200 | 377 | 1 | DE research network |

Added to `PERSONIO_COMPANIES` defaults in Settings / `.env.example`. Probed green but **not** defaulted: `plantura` (200, 1205 B, 3 jobs — retail/garden, not tech). Many guessed DE/CH tech slugs (e.g. n26, contentful, bitpanda, on-running, beekeeper) returned **404** on `*.jobs.personio.de`. Catalog **92** → ACTIVE `personio` connector (public listing; employer Recruiting API still credentialed separately).

### Free geo collectors insert evidence (2026-10-21, local compose)

Operator `POST /api/v1/sources/{id}/run` for newly wired public connectors (no credentials). First successful insert runs:

| When (UTC) | Key | source_id | run_id | status | received | inserted | notes |
|------------|-----|-----------|--------|--------|----------|----------|-------|
| 2026-10-20T22:49:31Z | `tecnoempleo` | 57 | 35 | succeeded | 80 | **80** | ES IT RSS |
| 2026-10-20T22:49:37Z | `le_forem` | 68 | 37 | succeeded | 200 | **180** | ODWB Wallonia dump |
| 2026-10-20T22:49:46Z | `mpsv` | 306 | 39 | succeeded | 300 | **289** | CZ JSON-LD stream + IT filter |

Later same-session re-runs (e.g. mpsv 81, le_forem 79) show `records_inserted=0` with high `received` — upsert/dedup against rows already present, not collector failure. DB `verification_status=ACTIVE`, `enabled=true` for all three.

**JobUp** (`jobup`, source_id=201): earlier runs 44/46/70 were `partial` (`rows=50` → API 422). Fixed `ROWS_PER_PAGE=20`; run **104** received **60** inserted **57**.

### Forced crawler tick (2026-10-20 ~22:49–22:54Z UTC)

Goal: `POST /api/v1/scheduler/run?force=true` so `GET /api/v1/ops/metrics` → `crawler.last_tick` is non-null and public ACTIVE sources may gain insert evidence. Local `.env` `API_KEY` was **empty** (auth open); header still sent. Host disk was ~100% full / Docker I/O flaky; API runs with `--reload`.

**HTTP client outcome:** two host `curl` attempts both failed with **curl exit 52 / empty reply** (~103s and ~129s). Error class: **empty HTTP reply / worker disconnect** (not a collector credentials failure). No API response body captured.

**Server-side tick (persisted despite empty HTTP):**

| Field | Value |
|-------|--------|
| `crawler_ticks.day` | `2026-10-20` |
| `crawler_ticks.status` | `succeeded` |
| `crawler_ticks.completed_at` | `2026-10-20T22:54:31.788432Z` |
| `ops/metrics` → `crawler.last_tick` | **non-null** (see below) |

`crawler.last_tick` snapshot (from live `GET /api/v1/ops/metrics` after tick):

| Field | Value |
|-------|--------|
| `day` | `2026-10-20` |
| `status` | `succeeded` |
| `idempotent` | `false` |
| `discovery_intents_enabled` | `10` |
| `focus_intents_enabled` | `8` |
| `discovery_intents_scheduled` | `3` |
| `focus_intents_scheduled` | `2` |
| `dump_ran` | `2` |
| `discovery_ran` | `3` |
| `focus_ran` | `1` |
| `calls` | `6` |
| `errors_count` | `0` |
| `skips` | `{budget: 2, missing_query: 1}` |
| `completed_at` (summary) | `2026-10-20T23:00:00+00:00` |

**Insert evidence in the force-tick window** (`collection_runs.started_at` ∈ `[2026-10-20T22:49Z, 2026-10-20T22:56Z)`, first `records_inserted > 0` for that connector — concurrent local `POST /sources/{id}/run` may overlap; tick summary itself only claims `calls=6`):

| Key | first run_id | inserted | completed_at (UTC) |
|-----|--------------|----------|--------------------|
| `tecnoempleo` | 35 | 80 | 22:49:34 |
| `ashby` | 36 | 267 | 22:49:46 |
| `le_forem` | 37 | 180 | 22:49:41 |
| `authentic_jobs` | 38 | 21 | 22:49:47 |
| `mpsv` | 39 | 289 | 22:49:58 |
| `devitjobs` | 40 | 400 | 22:49:55 |
| `dou_ua` | 41 | 50 | 22:49:59 |
| `getonbrd` | 42 | 50 | 22:50:00 |
| `greenhouse` | 43 | 1079 | 22:50:17 |
| `hasjob` | 45 | 17 | 22:50:18 |
| `helloworld_rs` | 47 | 11 | 22:50:18 |
| `hn_whoishiring` | 49 | 178 | 22:50:25 |
| `jobindex` | 51 | 20 | 22:50:28 |
| `jobweb_kenya` | 52 | 10 | 22:50:29 |
| `landing_jobs` | 53 | 49 | 22:50:31 |
| `lever` | 55 | 83 | 22:50:41 |
| `nofluffjobs` | 57 | 100 | 22:51:00 |
| `posao_hr` | 58 | 21 | 22:51:01 |
| `smartrecruiters` | 87 | 712 | 22:53:20 |
| `themuse` | 89 | 20 | 22:53:23 |
| `nav_arbeidsplassen` | 92 | 25 | 22:53:27 |
| `wanted` | 93 | 40 | 22:53:29 |
| `wantedly` | 94 | 8 | 22:53:32 |
| `arbetsformedlingen` | 95 | 100 | 22:53:36 |
| `duunitori` | 96 | 20 | 22:53:37 |
| `instahyre` | 101 | 35 | 22:53:52 |
| `jobup` | 104 | 57 | 22:54:58 |

Also saw additional inserts on connectors that **already** had prior insert-evidence (`jobicy` +90, `reed` +23, `working_nomads` +30). Left `status=running` after disconnects (not counted as inserts): `arbeitnow` runs 34/63, `smartrecruiters` 62, `arbetsformedlingen` 103. **Catalog ACTIVE flips this pass: none** (already ACTIVE public connectors). Credentialed scaffolds unchanged.

### Remaining ACTIVE free insert evidence (2026-10-21, local compose)

Goal: first `CollectionRun` rows with `records_inserted > 0` for public ACTIVE connectors still missing insert evidence (exclude credentialed scaffolds: adzuna, usajobs, france_travail, bundesagentur, jooble, findwork, careerjet, infojobs).

**DB selection:** `verification_status=ACTIVE`, `enabled=true`, non-credentialed `connector_type`, left join to runs with `records_inserted > 0`. Preferred geo keys (`landing_jobs`, `nofluffjobs`, `nav_arbeidsplassen`, `arbetsformedlingen`, `dou_ua`, `helloworld_rs`, `getonbrd`, `himalayas`) already had insert evidence from the ~22:49–22:54Z batch above; **jobup** run **104** also done. Remaining zero-evidence ACTIVE rows: `kalibrr`, `mycareersfuture`, `findmethatdamjob`, `personio` (+ `manual_import`, skipped for API collect).

Operator: sequential `POST /api/v1/sources/{id}/run?query=python` (~10s pause). Docker Desktop daemon was briefly unavailable; `docker compose up -d db redis api` recovered API before runs. No credentialed sources touched; no catalog ACTIVE flips.

| Key | source_id | run_id | status | received | inserted | updated | dup | notes |
|-----|-----------|--------|--------|----------|----------|---------|-----|-------|
| `kalibrr` | 204 | 122 | succeeded | 50 | **49** | 0 | 1 | SEA public job board API |
| `mycareersfuture` | 200 | 123 | succeeded | 50 | **35** | 0 | 15 | SG gov jobs API |
| `findmethatdamjob` | 351 | 124 | succeeded | 63 | **63** | 0 | 0 | NL public API |
| `personio` | 119 | 125 | succeeded | 1 | **1** | 0 | 0 | Public boards; default `PERSONIO_COMPANIES` in Settings — small payload this pass |

All four now have `has_insert_evidence` via `GET /api/v1/sources`. Only `manual_import` remains ACTIVE without insert runs (by design).

### Dev Global Jobs (LU/BG) — 2026-10-21

| Key | source_id | run_id | status | received | inserted | notes |
|-----|-----------|--------|--------|----------|----------|-------|
| `devglobaljobs` | 352 | 222 | succeeded | 26 | **15** | Free display API; default `DEVGLOBALJOBS_COUNTRIES=lu,bg`; attribution required; catalog ACTIVE id 198 |

Fills critical LU gap + BG Balkan bleed without scraping Jobs.bg (ADR-003).

### ViewJobs Australia — 2026-10-21

| Key | source_id | run_id | status | received | inserted | notes |
|-----|-----------|--------|--------|----------|----------|-------|
| `viewjobs` | 353 | 223 | succeeded | 37 | **37** | Free MCP `search_jobs` (python × metro places); all `country_code=AU`; catalog ACTIVE id 199 |

Also fixed ingest ISO tags: `country_code_from_collector_raw` + COUNTRY_HINTS (BG/AU/…). Re-run `devglobaljobs` **224** updated 15 rows → `BG=8`, `LU=7` (was `unknown` for BG).

### okemprego Portugal — 2026-10-21

| Key | source_id | run_id | status | received | inserted | notes |
|-----|-----------|--------|--------|----------|----------|-------|
| `okemprego` | 354 | 225 | succeeded | 150 | **148** | Free public API (`/api/v1/jobs`); default `OKEMPREGO_COUNTRIES=pt` + `category=it-data`; all `country_code=PT`; catalog ACTIVE id 200 |

Complements `landing_jobs` for Iberia IT (ADR-003: cite canonical listing URL; no IEFP scrape).

### Canada Job Bank open data — 2026-10-21

| Key | source_id | run_id | status | received | inserted | notes |
|-----|-----------|--------|--------|----------|----------|-------|
| `jobbank_ca` | 355 | 228 | succeeded | 200 | **179** (+21 updated) | ESDC monthly CSV via CKAN (OGL-Canada); IT via NOC21 212/2222 + title keywords; all `country_code=CA`; catalog ACTIVE id 201 |

Snapshot posting IDs often 410 on `/jobposting/{id}` — URL is Job Bank search deep-link + `fmi_snap` for uniqueness. No HTML scrape.

## Rejected

| Source | Reason |
|--------|--------|
| Google for Jobs / JobPosting docs | Publisher structured data, not a pull API |
| Common Crawl | Not an authorized job harvest path for this product |

## Duplicates corrected

| Catalog id | Points to |
|------------|-----------|
| 42 InfoJobs Spain | 25 InfoJobs |
| 108 USAJOBS (stats ref) | 7 USAJOBS |
| 120/121 agency stats refs | 30/31 |
| 130 Stats NZ | 112 |
| 169 Google Job Posting docs | 13 |

## Legal

No CAPTCHA/login/paywall bypass. ATS connectors only hit **public** board endpoints for configured tenants.
