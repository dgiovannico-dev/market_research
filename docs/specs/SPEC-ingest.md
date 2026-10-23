# Spec: ingest

## Objective

Collect and persist job postings from authorized/public sources and manual imports, with deduplication, provenance, sync history, and an explicit connector status model. Catalog lifecycle and verification procedure: [SPEC-sources.md](SPEC-sources.md).

## In scope

### Registry & schema

- `sources` with `connector_status` (`enabled` | `requires_credentials` | `unsupported`) plus catalog fields (`catalog_id`, `verification_status`, `category`, docs URLs).
- `source_verifications` (or equivalent) for probe/evidence history.
- Collection / sync runs with counts, duplicates, error summaries.
- Job snapshots / provenance: do not silently overwrite prior observations without history.

### Collectors (ACTIVE when verified)

| Key | Access |
|-----|--------|
| `remotive` | Public REST |
| `arbeitnow` | Public REST |
| `remoteok` | Public REST (attribution) |
| `working_nomads` | Public REST |
| `weworkremotely` | Public RSS |
| `themuse` | Public REST |
| `jobicy` | Free public remote API (attribution) |
| `himalayas` | Free public jobs API |
| `hn_whoishiring` | HN Algolia public API (Who is hiring comments) |
| `devitjobs` | Free jobsLight JSON (`uk`/`com` hosts) |
| `nofluffjobs` | Free CEE posting dump (capped + query filter; often B2B hourly) |
| `reed` | Free public RSS (`/jobs/rss`); optional `REED_API_KEY` for JSON API |
| `getonbrd` | Free LATAM tech JSON (`/api/v0/search/jobs`) |
| `mycareersfuture` | Free Singapore government jobs API v2 |
| `jobup` | Free Swiss public search JSON |
| `nav_arbeidsplassen` | Free Norwegian PES stillinger search JSON |
| `landing_jobs` | Free EU tech jobs JSON (EUR salary bands) |
| `kalibrr` | Free SEA job board search JSON |
| `dou_ua` | Free Ukrainian IT category RSS |
| `authentic_jobs` | Free design/dev jobs RSS (FeedBurner) |
| `wantedly` | Free Japan projects/jobs JSON |
| `duunitori` | Free Finland jobentries JSON |
| `jobindex` | Free Danish jobs RSS |
| `wanted` | Free Korea jobs JSON (v4) |
| `instahyre` | Free India tech job search JSON |
| `hasjob` | Free India/tech jobs JSON board |
| `helloworld_rs` | Free Serbian IT jobs RSS |
| `posao_hr` | Free Croatian jobs RSS |
| `jobweb_kenya` | Free Kenya jobs RSS |
| `greenhouse` | Public board API (configured tenants) |
| `lever` | Public postings API (configured sites) |
| `personio` | Public `search.json` per slug on `*.jobs.personio.de` |
| `ashby` | Public boards when `ASHBY_ORGS` set |
| `smartrecruiters` | Public company postings when `SMARTRECRUITERS_COMPANIES` set |
| `arbetsformedlingen` | Public JobTech JobSearch (Sweden PES, no key) |
| `adzuna` | Job Search API when `ADZUNA_APP_ID` + `ADZUNA_APP_KEY` set |
| `usajobs` | Federal search when `USAJOBS_API_KEY` + `USAJOBS_USER_AGENT` set |
| `france_travail` | Offres v2 when `FRANCE_TRAVAIL_CLIENT_ID` + `SECRET` set |
| `bundesagentur` | Jobsuche when `BUNDESAGENTUR_API_KEY` set |
| `jooble` | Jooble search when `JOOBLE_API_KEY` set |
| `careerjet` | Careerjet Partner v4 when `CAREERJET_API_KEY` + `CAREERJET_USER_IP` set |
| `infojobs` | InfoJobs `GET /api/1/offer` when `INFOJOBS_CLIENT_ID` + `INFOJOBS_CLIENT_SECRET` set |
| `manual_import` | CSV / JSON / XLSX upload |

### Support paths

- FX: Frankfurter + ECB (`GET /api/v1/fx/rates`) for currency normalization helpers.
- Dedup keys: source+native id, canonical URL, title/company/location signals, description hash.
- Multi-source links: keep references when the same posting appears on multiple sources.

### Demand Compass sync (normative with research-intents)

Topic-scoped collection is owned by **discovery + focus intents**, not env defaults:

- **Daily crawlers** (scheduled): dump/feed once → discovery watchlist → user focus intents.
- Search-mode collectors require explicit `query` / intent text; **no** silent `*_DEFAULT_QUERY` fallback.
- Scheduled runs SHOULD set `collection_runs.query_id` and `jobs.query_id` when an intent drove the fetch.

Full contract: [SPEC-research-intents.md](SPEC-research-intents.md) · [ADR-007](../decisions/ADR-007-query-first-sync.md) · [Demand Compass](../ideas/freelance-demand-compass.md).

### Rate / compensation fields (separate; never invent)

Employee salary · freelance rate · hourly · daily · monthly · project budget · agreed rate if known · undeclared (`NULL`).

## Out of scope

- LinkedIn / Malt / Indeed / Upwork / Adzuna / USAJOBS / PES APIs without authorized credentials.
- Bypass of auth, CAPTCHA, paywall, or ToS.
- Treating Google for Jobs or Common Crawl as pull job APIs.
- Declaring `ACTIVE` without live records.
- Using Settings topic defaults as the product “aim” for daily sync.

## Acceptance criteria

- [x] Enabled sources run via `POST /api/v1/sources/{id}/run` and insert/update jobs.
- [x] Catalog-synced non-runnable sources stay non-runnable with explicit status in UI/API.
- [x] Import endpoint accepts sample CSV under `data/samples/`.
- [x] Duplicates increment `duplicates_detected` / update existing canonical rows rather than silent double-count.
- [x] Live collector tests cover ACTIVE public connectors where feasible.
- [ ] Credentialed connectors (Adzuna, USAJOBS, …) become runnable only after real keys + tests ([global sources plan](../superpowers/plans/2026-10-20-global-sources.md)).
- [ ] Search-mode collectors skip with `missing_query` when no intent/query is provided (no env topic substitute).
- [x] Daily scheduler fans out enabled intents and persists `query_id` provenance ([query-first plan](../superpowers/plans/2026-10-20-query-first-daily-sync.md)).

## Commands

```bash
curl -X POST http://localhost:8000/api/v1/sources/{id}/run
curl -F "file=@data/samples/jobs_sample.csv" http://localhost:8000/api/v1/imports
curl http://localhost:8000/api/v1/sources/catalog/summary
curl "http://localhost:8000/api/v1/fx/rates?base=EUR&symbols=USD,CHF"
POST /api/v1/admin/seed   # sync catalog into DB
```

## Key paths

- `backend/app/collectors/`
- `backend/app/ingestion/`
- `backend/app/scheduler/runner.py`
- `backend/app/fx/rates.py`
- `backend/app/sources/catalog.py`
- `backend/app/storage/seed.py`
- `backend/alembic/versions/` (incl. catalog/verification migration)
- `frontend/app/sources/page.tsx`
- Evidence: [../sources/VALIDATION_REPORT.md](../sources/VALIDATION_REPORT.md)
- Query-first: [SPEC-research-intents.md](SPEC-research-intents.md), [../superpowers/plans/2026-10-20-query-first-daily-sync.md](../superpowers/plans/2026-10-20-query-first-daily-sync.md)
