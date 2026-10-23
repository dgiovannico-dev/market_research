# Credentialed connectors

Scaffolds registered in `COLLECTORS` that stay `NEEDS_CREDENTIALS` until a **live** run persists jobs. Keys alone never flip catalog `ACTIVE`.

Prefer free public connectors first (`jobicy`, `himalayas`, `hn_whoishiring`, `devitjobs`, `nofluffjobs`, `getonbrd`, `mycareersfuture`, `jobup`, `nav_arbeidsplassen`, `nav_stilling_feed`, `landing_jobs`, `kalibrr`, `dou_ua`, `authentic_jobs`, `wantedly`, `duunitori`, `jobindex`, `wanted`, `instahyre`, `hasjob`, `helloworld_rs`, `posao_hr`, `jobweb_kenya`, `tecnoempleo`, `le_forem`, `mpsv`, `findmethatdamjob`, `reed` RSS, Remotive, Remote OK, WWR, Arbetsförmedlingen, ATS boards) before enabling paid aggregators. Do not scrape the HTML of paid boards as a substitute for missing API keys ([ADR-003](../decisions/ADR-003-authorized-connectors-only.md)). StepStone/XING/Careers24 `/jobs/rss` URLs returned HTML — not used. Wuzzuf public JSON was closed/expired-heavy — not ACTIVE.

| Key | Env | Auth |
|-----|-----|------|
| `adzuna` | `ADZUNA_APP_ID`, `ADZUNA_APP_KEY` (+ optional `ADZUNA_COUNTRIES` / `ADZUNA_COUNTRY`) | Query params; multi-country paths per collect |
| `usajobs` | `USAJOBS_API_KEY`, `USAJOBS_USER_AGENT` | Header `Authorization-Key` + User-Agent email; optional `USAJOBS_JOB_CATEGORY_CODE` (e.g. `2210` IT Management) → `JobCategoryCode` |
| `france_travail` | `FRANCE_TRAVAIL_CLIENT_ID`, `FRANCE_TRAVAIL_CLIENT_SECRET` | OAuth2 client credentials |
| `bundesagentur` | `BUNDESAGENTUR_API_KEY` | Header `X-API-Key` (Jobsuche) |
| `jooble` | `JOOBLE_API_KEY` | POST `/api/{key}` |
| `findwork` | `FINDWORK_API_KEY` (+ optional `FINDWORK_LOCATION`) | Token header (`Authorization: Token …`); fail-closed without key |
| `findajob_dwp` | `FINDAJOB_DWP_API_ID`, `FINDAJOB_DWP_API_KEY` (+ optional `FINDAJOB_DWP_LOCATION`) | Query `api_id`/`api_key` on `findajob.dwp.gov.uk/api/search`; fail-closed without keys |
| `freelancer` | `FREELANCER_OAUTH_TOKEN` (+ optional `FREELANCER_API_BASE`) | Bearer + `Freelancer-OAuth-V1`; `GET …/projects/0.1/projects/active/` |
| `careerjet` | `CAREERJET_API_KEY`, `CAREERJET_USER_IP` (+ optional `CAREERJET_LOCALES`, `CAREERJET_LOCATION`, `CAREERJET_CONTRACT_TYPE`) | Basic auth; GET `search.api.careerjet.net/v4/query` |
| `infojobs` | `INFOJOBS_CLIENT_ID`, `INFOJOBS_CLIENT_SECRET` (+ optional `INFOJOBS_COUNTRY`, `INFOJOBS_MAX_RESULTS`) | HTTP Basic; GET `https://api.infojobs.net/api/1/offer` |

`reed` is **free via public RSS** (`/jobs/rss?keywords=`). Optional `REED_API_KEY` enables the richer JSON API — not required for ACTIVE. Prefer keyed Reed when available for salary/contract fields.

Optional FX (not a job connector): `OPEN_EXCHANGE_RATES_APP_ID` → overlay on `GET /api/v1/fx/rates`.

## Secrets storage (DB preferred)

Connector API secrets may be stored **encrypted at rest** in Postgres (`source_credentials`), with Fernet key `CREDENTIALS_MASTER_KEY` only in env (never in the DB). Resolution order: **DB row wins** when present; otherwise env fallback (bootstrap / Compose).

| Env (always) | Purpose |
|--------------|---------|
| `CREDENTIALS_MASTER_KEY` | Fernet key — generate with `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"` |
| `OPS_API_TOKEN` | Required for PUT/DELETE/GET credential-fields (`X-Ops-Token` or `Authorization: Bearer`) |

**Ops UI:** Fonti → scaffold row → “Imposta chiavi” / “Set keys”. Paste `OPS_API_TOKEN` (kept in `sessionStorage` for the tab only). API never returns plaintext secrets — only `credentials_present`, `credentials_source` (`db` \| `env` \| `none`), and field set/unset flags.

**API:**

- `GET /api/v1/ops/connectors` — booleans + `credentials_source` (no token)
- `GET /api/v1/ops/connectors/{key}/credential-fields` — field metadata (**token**)
- `PUT /api/v1/ops/connectors/{key}/credentials` — body `{ "fields": {…}, "ops_label": "ops-ui" }` (**token**)
- `DELETE /api/v1/ops/connectors/{key}/credentials` — drop DB row; env fallback resumes (**token**)

Non-secret config (countries, locations, scopes) stays in env / Settings.

## Enable

1. Set `CREDENTIALS_MASTER_KEY` + `OPS_API_TOKEN` in `.env` (see `.env.example`). Optionally still set connector env keys as fallback.
2. `alembic upgrade head` / restart API so seed syncs `Source.enabled`.
3. Save secrets via Fonti UI or `PUT …/credentials`, **or** use env vars alone.
4. `POST /api/v1/sources/{id}/run`.
5. Promote DB status only with evidence:
   `python scripts/promote_source_active.py --connector-key <key>`
   (requires a succeeded CollectionRun with `records_inserted > 0`).
6. Update `generate_source_catalog.py` + regenerate catalog; note evidence in [VALIDATION_REPORT.md](VALIDATION_REPORT.md).

## Notes

- France Travail: create an app on francetravail.io and subscribe to Offres d'emploi v2. Distribution rules can change — verify current access.
- Bundesagentur: Jobsuche **v6** (`/pc/v6/jobs`) documented via [bund.dev](https://jobsuche.api.bund.dev/); confirm reuse terms for your deployment before production. A keyed probe returned job rows; catalog stays `NEEDS_CREDENTIALS` until you enable the key and promote after your own live ingest.
- Careerjet: publisher account + API key at [careerjet.com/partners/api](https://www.careerjet.com/partners/api/). Each query requires `user_ip` and `user_agent` (set `CAREERJET_USER_IP`; default UA in `.env.example`). Optional `CAREERJET_LOCALES` defaults to IT/DE/CH/LU locale codes. Scaffold only until a succeeded run with inserts + promote.
- Findwork: self-serve token at [findwork.dev/developers](https://findwork.dev/developers/). Fail-closed without `FINDWORK_API_KEY`.
- Find a Job UK DWP: request `api_id` / `api_key` via [UK API Catalogue / DWP Find a Job](https://www.api.gov.uk/dwp/find-a-job/). Fail-closed without both env vars.

## Residual blockers (keyed ACTIVE)

| Connector | Blocker |
|-----------|---------|
| All credentialed scaffolds | DB encrypted secrets and/or env credentials must be set; empty → fail-closed / non-runnable. Writes require `OPS_API_TOKEN` + `CREDENTIALS_MASTER_KEY`. |
| `careerjet` | Publisher API key + valid `CAREERJET_USER_IP` per partner terms |
| `infojobs` | Register app on developer.infojobs.net; bulk storage/redistribution may need partner agreement (`gestiondatos@infojobs.net`) |
| Promote gate | Needs succeeded `CollectionRun` with `records_inserted > 0` |
| Catalog parity | After promote: update `generate_source_catalog.py` + regenerate `catalog.json` |
| France Travail | May also need Emploi Store / Offres v2 subscription |
| Bundesagentur | Confirm API reuse terms for your deployment |

**Re-check 2026-10-20:** compose API reported `credentials_present=false` for adzuna, usajobs, france_travail, bundesagentur, jooble, findwork, careerjet, infojobs; DB had zero succeeded insert runs for keyed scaffolds; fail-closed collect returned `records=0`. No ACTIVE promote this pass.

**2026-10-21:** added `findajob_dwp` + `freelancer` scaffolds; still fail-closed until keys/token + live inserts.
