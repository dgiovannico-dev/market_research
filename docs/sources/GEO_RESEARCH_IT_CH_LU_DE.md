# Geo research: Italy · Switzerland · Luxembourg · Germany

**Audience:** FMI Demand Compass (IT freelancers / tech / remote / B2B signals)  
**Date:** 2026-10-21  
**Method:** Primary sources only (official portals, developer docs, open-data licenses, WSDL/OpenAPI). No invented API keys. Scraping LinkedIn/Indeed is out of scope (see [ADR-003](../decisions/ADR-003-authorized-connectors-only.md)).

## Repo baseline (already in collectors)

| Connector | Geo relevance | Status note |
|-----------|---------------|-------------|
| `arbeitnow` | DE-heavy EU tech / remote / visa tags | ACTIVE, keyless |
| `jobup` | Switzerland (JobCloud / jobup.ch public search) | ACTIVE, keyless |
| `bundesagentur` | Germany PES Jobsuche | Scaffold; `BUNDESAGENTUR_API_KEY`; **reuse terms are restricted** |
| `adzuna` | Multi-country aggregator (`ADZUNA_COUNTRY`) | Scaffold; supports **it / de / ch** among others; **not lu** |
| `jooble` | Per-country keys (`it.jooble.org`, `de.jooble.org`, …) | Scaffold; free tier **500 lifetime requests / key** |
| `landing_jobs` | EU tech (PT-heavy, some EU remote) | ACTIVE |
| `nofluffjobs` | CEE IT + B2B hourly (spill into DE/remote) | ACTIVE |
| `remotive` / `remoteok` / `himalayas` / `jobicy` / ATS boards | Global remote | ACTIVE — filter by location, not national PES depth |
| `france_travail` | FR only (cross-border LU/CH relevance via EURES, not a CH/IT/DE fill) | Scaffold |

Gaps this research targets: **Italy national board**, **Luxembourg live + open data**, **Swiss PES vs commercial**, **DE legal clarity**, **partner aggregators with IT/CH/LU locales**.

---

## Top recommendations (ranked)

| Rank | Source | Pri | One-line why |
|------|--------|-----|--------------|
| 1 | **Adzuna** (`it` / `de` / `ch`) | P0 | Documented partner JSON API; scaffold already in-repo; best single keyed path for IT+DE+CH IT categories. |
| 2 | **InfoJobs API** (Italy) | P0 | Official developer program + `GET /api/1/offer`; Italy’s largest private board with substantial IT inventory. |
| 3 | **Careerjet Partner API** | P0 | Documented v4 search; locales `it_IT`, `de_DE`, `de_CH`/`fr_CH`, `fr_LU` cover all four markets. |
| 4 | **JobUp** (keep / deepen queries) | P0 | Already ACTIVE Swiss public JSON; deepen IT/remote query set before adding jobs.ch twin. |
| 5 | **Arbeitnow** (keep) | P0 | Already ACTIVE DE-heavy ATS-sourced tech board; remote + visa filters map well to Compass personas. |
| 6 | **ADEM skills–vacancies open data** (LU) | P1 | CC0 CSV microdata from official open-data portal; skill/occupation demand intel (not live postings). |
| 7 | **jobs.lu JobWS** (`SearchJobs`) | P1 | Documented SOAP search with `key` param; commercial LU board with IT/finance density. |
| 8 | **Personio public boards** (DACH allowlist) | P1 | Per-tenant `search.json` / XML feeds; deep mid-market DE/CH/AT tech employers without HTML scrape. |
| 9 | **Jooble** (`it` + `de` keys) | P1 | Scaffold exists; use sparingly (500 lifetime req/key) as Italy/Germany backfill, not primary poller. |
| 10 | **Ministero del Lavoro SPARQL** (`mi:OffertaAttiva`) | P1 | Official open Linked Data for Italian active offers; good PES signal if endpoint healthy. |
| 11 | **Bundesagentur Jobsuche** (legal review) | P1→P2 | Largest DE corpus + connector ready, but BA Nutzungsbedingungen restrict automation/redistribution — counsel before production Compass use. |
| 12 | **Job-Room SPA `_search`** (CH PES) | P2 | Public JSON used by arbeit.swiss UI; **not** the documented employer Jobs API — treat as fragile / ToS-sensitive until SECO confirms reuse. |

---

## Source dossiers

### 1. Adzuna Job Search API — P0

| Field | Detail |
|-------|--------|
| **Country/region** | Italy (`it`), Germany (`de`), Switzerland (`ch`). Luxembourg **not** in supported country path set. |
| **Official site** | https://www.adzuna.com/ / country sites (e.g. adzuna.it, adzuna.de, adzuna.ch) |
| **Access mode** | Partner JSON API (`GET /v1/api/jobs/{country}/search/{page}`) |
| **Docs** | https://developer.adzuna.com/ · https://developer.adzuna.com/docs/search · https://api.adzuna.com/v1/doc |
| **Auth** | `app_id` + `app_key` query params (developer account). Repo: `ADZUNA_APP_ID`, `ADZUNA_APP_KEY`, `ADZUNA_COUNTRY`. |
| **IT / tech substantial?** | Yes — IT Jobs category filter; large national inventories for IT/DE/CH. |
| **Repo** | `backend/app/collectors/adzuna.py` — enable multi-country runs (rotate `ADZUNA_COUNTRY` or extend collector). |
| **Notes** | Prefer over Jooble for volume (Jooble free quota is tiny). Descriptions are snippets. |

### 2. InfoJobs Developer API (Italy) — P0

| Field | Detail |
|-------|--------|
| **Country/region** | Italy (InfoJobs.it / Adevinta Jobs). Spain sister brand exists; this dossier is **IT**. |
| **Official site** | https://www.infojobs.net/ (IT product) · Developer: https://developer.infojobs.net/ |
| **Access mode** | Partner REST API (JSON or XML) |
| **Docs** | https://developer.infojobs.net/documentation/quick-start/index.xhtml · operations: https://developer.infojobs.net/documentation/operation-list/index.xhtml · ToS: https://developer.infojobs.net/legal/legal/terms-of-use.xhtml |
| **Auth** | Register app → Client ID + Client Secret; HTTP Basic on `https://api.infojobs.net`. Job search: `GET /api/1/offer`, detail `GET /api/1/offer/{offerId}`. |
| **IT / tech substantial?** | Yes — Italy’s primary private employment board; Informatica / engineering volume is material for Compass. |
| **Caveats** | Commercial storage/redistribution and high volume may require Partner agreement (`gestiondatos@infojobs.net`). Do **not** scrape the HTML site. |

### 3. Careerjet Partner API — P0

| Field | Detail |
|-------|--------|
| **Country/region** | Locales include `it_IT`, `de_DE`, `de_CH`, `fr_CH`, `fr_LU` (and more). Covers **all four** target markets. |
| **Official site** | https://www.careerjet.com/ (and country TLDs) |
| **Access mode** | Partner JSON API |
| **Docs** | https://www.careerjet.com/partners/api/ |
| **Auth** | Publisher account API key; HTTP Basic (key as username, empty password). Endpoint: `https://search.api.careerjet.net/v4/query`. Requires `user_ip` + `user_agent` on each call. |
| **IT / tech substantial?** | Aggregator — tech share varies by locale; useful for contract (`contract_type=c`) and keyword filters (`software`, `freelance`, …). |
| **Repo** | `backend/app/collectors/careerjet.py` — scaffold; `CAREERJET_API_KEY` + `CAREERJET_USER_IP`. Catalog `NEEDS_CREDENTIALS` until live promote. |
| **Caveats** | Affiliate/publisher terms; typically for displaying search results, not bulk archival — confirm license for analytics store. |

### 4. JobUp.ch public search — P0 (already ACTIVE)

| Field | Detail |
|-------|--------|
| **Country/region** | Switzerland (FR/DE/IT/EN surfaces via JobCloud family). |
| **Official site** | https://www.jobup.ch/ |
| **Access mode** | Public JSON used by product UI: `GET https://www.jobup.ch/api/v1/public/search` |
| **Docs** | No formal OpenAPI; validated live in [VALIDATION_REPORT.md](VALIDATION_REPORT.md). Employer-facing JobCloud feeds: https://www.jobcloud.ch/c/de-ch/technical-solution/ |
| **Auth** | None for public search. |
| **IT / tech substantial?** | Yes for CH market; filter with IT keywords. |
| **Repo** | `jobup` collector ACTIVE. |
| **Note on jobs.ch** | Same JobCloud family; catalog lists `jobs.ch` UNDER_REVIEW. Public search host `job-search-api.jobs.ch` appears in third-party writeups — **prefer JobUp (proven)**; treat jobs.ch twin as optional duplicate, not a new PES. |

### 5. Arbeitnow Job Board API — P0 (already ACTIVE)

| Field | Detail |
|-------|--------|
| **Country/region** | Europe / Germany-heavy; remote + UK sister host. |
| **Official site** | https://www.arbeitnow.com/ |
| **Access mode** | Public JSON API (keyless) |
| **Docs** | https://www.arbeitnow.com/blog/job-board-api · endpoint `https://www.arbeitnow.com/api/job-board-api` |
| **Auth** | None. Optional `visa_sponsorship=true|false`. |
| **IT / tech substantial?** | High — ATS-sourced (Greenhouse, SmartRecruiters, Join, Teamtailor, Recruitee, Comeet). |
| **Repo** | `arbeitnow` ACTIVE. Keep as DE/remote backbone. |

### 6. ADEM — Skills required in job vacancies (open data) — P1

| Field | Detail |
|-------|--------|
| **Country/region** | Luxembourg |
| **Official site** | https://adem.public.lu/ · dataset: https://data.public.lu/en/datasets/skills-required-in-adem-job-vacancies/ |
| **Access mode** | Open data CSV downloads (CC0), updated ~quarterly |
| **Docs** | Dataset page + methodology paper linked from portal; ESCO skill URIs; ROME occupation codes. |
| **Auth** | None. |
| **IT / tech substantial?** | Skills/occupation/NACE fields enable IT-sector demand series; **active ads are not published** (closed vacancies after ~2 months). |
| **Priority rationale** | Best **legal** LU labour-demand signal without scraping Moovijob. Pair with live board (jobs.lu / EURES browser) for postings. |
| **Live LU postings note** | ADEM publishes declared vacancies on EURES: https://adem.public.lu/en/jobboard.html — no ADEM public machine API for live offers found. |

### 7. jobs.lu JobWS (SOAP) — P1

| Field | Detail |
|-------|--------|
| **Country/region** | Luxembourg |
| **Official site** | https://en.jobs.lu/ · employer API host https://en.employers.jobs.lu/ |
| **Access mode** | Partner SOAP web service (`JobWS.asmx`) — **not** scrape |
| **Docs** | ASMX operation pages, e.g. https://en.employers.jobs.lu/JobWS.asmx?op=SearchJobs · WSDL: https://en.employers.jobs.lu/JobWS.asmx?WSDL |
| **Auth** | `SearchJobs` accepts a `key` string; posting ops use employer login/password. Obtain key from jobs.lu partnership — **do not invent**. |
| **IT / tech substantial?** | Strong LU IT/finance mix; filter `keywords` + category IDs. |
| **Caveats** | Legacy SOAP; confirm commercial redistributability with publisher. |

### 8. Personio public career boards (ATS) — P1

| Field | Detail |
|-------|--------|
| **Country/region** | DACH-heavy (DE/AT/CH mid-market); some NL/IT tenants |
| **Official site** | https://www.personio.com/ |
| **Access mode** | Per-company **public** JSON/XML career feeds (ATS pattern, like Greenhouse allowlist) |
| **Docs** | Recruiting XML: https://github.com/personio/api-docs/blob/master/personio-recruiting-api.yaml · Support overview: https://support.personio.de/hc/en-us/articles/360000314338-Overview-of-the-Personio-Recruiting-API · Authenticated company API: https://developer.personio.de/ |
| **Auth** | Public listing: none — `GET https://{company}.jobs.personio.de/search.json` or `/xml?language=en`. Company Recruiting API needs tenant token (employer-owned). |
| **IT / tech substantial?** | High for DE/CH product/engineering roles when allowlist is curated. |
| **Repo fit** | Extend ATS strategy in [ATS_TENANTS.md](ATS_TENANTS.md) with a Personio slug allowlist (no HTML scrape). Listing endpoint often lacks description/pay — good for demand counts, weaker for rate extraction. |

### 9. Jooble REST API — P1 (scaffold; quota-limited)

| Field | Detail |
|-------|--------|
| **Country/region** | Per-domain keys: e.g. https://it.jooble.org/api/about , https://de.jooble.org/api/about . CH/LU domains exist as Jooble sites; register per domain. |
| **Official site** | Regional Jooble TLDs |
| **Access mode** | Partner REST API `POST https://{country}.jooble.org/api/{api_Key}` |
| **Docs** | https://help.jooble.org/en/support/solutions/articles/60001448238-rest-api-documentation |
| **Auth** | Country-specific API key in URL path. |
| **IT / tech substantial?** | Aggregator — usable with IT keywords; quality uneven. |
| **Repo** | `jooble` scaffold. Free plan: **500 lifetime requests per key** — unsuitable as primary crawler. |

### 10. Ministero del Lavoro / Cliclavoro Linked Open Data — P1

| Field | Detail |
|-------|--------|
| **Country/region** | Italy |
| **Official site** | https://www.lavoro.gov.it/ · Cliclavoro https://www.cliclavoro.gov.it/ · Open Data https://www.lavoro.gov.it/strumenti-e-servizi/Open-Data/Pagine/default |
| **Access mode** | Official SPARQL endpoint → JSON/CSV/XML (open data) |
| **Docs** | Query examples: https://www.lavoro.gov.it/strumenti-e-servizi/open-data/pagine/accesso-ai-dati (`mi:OffertaAttiva`, Milan filter examples). CKAN-style catalog https://dati.gov.it/api for metadata. |
| **Auth** | None for SPARQL. |
| **IT / tech substantial?** | Mixed national vacancies; filter by description / profession labels for Informatica. Weaker than InfoJobs for pure tech density. |
| **Caveats** | `dati.lavoro.gov.it` CKAN portal has been observed in maintenance; SPARQL availability can degrade — treat as **fragile ops**, still legally preferred over scrape. ANPAL DOL (MyANPAL) is a **web portal**, not a public vacancy API. |

### 11. Bundesagentur für Arbeit — Jobsuche — P1→P2 (legal gate)

| Field | Detail |
|-------|--------|
| **Country/region** | Germany |
| **Official site** | https://www.arbeitsagentur.de/ |
| **Access mode** | JSON REST used by BA apps; community OpenAPI at https://jobsuche.api.bund.dev/ · base `https://rest.arbeitsagentur.de/jobboerse/jobsuche-service` · `GET /pc/v6/jobs` |
| **Docs** | https://jobsuche.api.bund.dev/ · OpenAPI https://github.com/bundesAPI/jobsuche-api |
| **Auth** | Header `X-API-Key` (public client id documented as `jobboerse-jobsuche`). Repo expects `BUNDESAGENTUR_API_KEY`. |
| **IT / tech substantial?** | Very large; `berufsfeld=Informatik`, `angebotsart=2` (Selbständigkeit), `arbeitszeit=ho` useful for freelance/remote signals. |
| **Legal / ToS** | BA [Nutzungsbedingungen](https://www.arbeitsagentur.de/nutzungsbedingungen) prohibit robots/spidering and using interfaces contrary to intended purpose for data collection/analysis. Data is **not** open data. Community clients warn against commercial redistribution. **Compass production use needs explicit legal clearance** — keep scaffold for authorized/personal placement use only until cleared. |
| **Repo** | `bundesagentur` scaffold + notes in [CREDENTIALED_CONNECTORS.md](CREDENTIALED_CONNECTORS.md). Prefer Arbeitnow + Adzuna `de` for day-to-day DE tech intel if BA reuse is blocked. |

### 12. Job-Room / arbeit.swiss (SECO) — P2

| Field | Detail |
|-------|--------|
| **Country/region** | Switzerland (national PES / Stellenmeldepflicht bank) |
| **Official site** | https://www.job-room.ch/ · https://www.arbeit.swiss/ |
| **Access modes** | **(A)** Documented **employer** Jobs API (publish vacancies): https://api.job-room.ch/jobAdvertisements/v1 — docs https://test-api.job-room.ch/api-docs/jobAdvertisements/v1/ — credentials via `jobroom-api@seco.admin.ch`. **Not a public search API.** **(B)** SPA backend `POST https://www.job-room.ch/jobadservice/api/jobAdvertisements/_search` — undocumented public JSON used by the official UI; third parties scrape it. |
| **Auth** | (A) Basic auth after SECO approval. (B) None observed — still **fragile / ToS risk** without written SECO permission. |
| **IT / tech substantial?** | Broad occupations; IT present but not tech-board density of JobUp. Unique for **mandatory reported** vacancies. |
| **Recommendation** | Ask SECO for read/search partnership. Until then, do **not** ship a production connector on (B). Use JobUp for CH commercial tech demand. |

---

## Secondary / conditional sources

| Source | Mode | Verdict for Compass |
|--------|------|---------------------|
| **EURES portal search** | EU official portal https://europa.eu/eures/ — Member/Partner APIs via ECO; community reverse-engineered `POST …/jv-search/search` is **unofficial** | P2: pursue **official** EURES Member/Partner access for LU/IT/DE feeds; do not depend on undocumented public POST. |
| **jobs.ch public search** | Same JobCloud family as JobUp | P2 duplicate of JobUp unless coverage delta proven. |
| **Malt** | https://api.malt.com/ — billing + SCIM only; **no** public mission/search API | Blocked for demand ingest; marketplace gap remains ([COVERAGE_GAPS.md](COVERAGE_GAPS.md)). |
| **Moovijob (LU)** | HTML job board, no public API/RSS found | Scrape-only → **reject** under ADR-003. |
| **Talent.io** | Matching marketplace FR/DE/… — no public jobs API found | Reject for ingest; optional partnership Later. |
| **StepStone / XING HTML or fake RSS** | Previously probed HTML-as-RSS | Reject (see CREDENTIALED_CONNECTORS). |
| **Indeed / LinkedIn scrape** | — | Reject. |

---

## Priority matrix by country

| Country | P0 path | P1 path | Avoid |
|---------|---------|---------|-------|
| **IT** | InfoJobs API + Adzuna `it` + Careerjet `it_IT` | Ministero SPARQL `OffertaAttiva` | Cliclavoro HTML scrape; LinkedIn |
| **CH** | JobUp (live) + Adzuna `ch` + Careerjet `de_CH`/`fr_CH` | Personio CH tenants; SECO Jobs API **if** read access granted | Job-Room `_search` without permission; jobs.ch HTML |
| **LU** | Careerjet `fr_LU` | ADEM CC0 skill CSVs + jobs.lu JobWS key | Moovijob scrape |
| **DE** | Arbeitnow (live) + Adzuna `de` + Careerjet `de_DE` | Personio DE allowlist; Jooble `de` (quota) | BA Jobsuche commercial use without clearance; StepStone/XING scrape |

---

## Suggested next engineering steps (no secrets invented)

1. **Adzuna multi-country:** run/probe `it`, `de`, `ch` with existing keys; document category=`it-jobs` filters for Compass.
2. **InfoJobs:** register developer app; spike `GET /api/1/offer` with IT keywords; legal review of storage ToS.
3. **Careerjet:** publisher signup; spike locales `it_IT`, `de_DE`, `de_CH`, `fr_LU` with `contract_type=c`.
4. **LU:** download latest ADEM CSV for skill demand baseline; contact jobs.lu for JobWS `SearchJobs` key.
5. **Personio:** curate DE/CH company slug allowlist + probe `search.json` (mirror Greenhouse process).
6. **BA Jobsuche:** legal memo before promoting beyond scaffold; until then lean on Arbeitnow + Adzuna DE.
7. **Job-Room:** email `jobroom-api@seco.admin.ch` asking whether a **read/search** product API exists for analytics partners (employer publish API alone is insufficient).

---

## Citation index (primary)

- Adzuna search docs — https://developer.adzuna.com/docs/search  
- InfoJobs developer — https://developer.infojobs.net/  
- Careerjet partners API — https://www.careerjet.com/partners/api/  
- Arbeitnow API article — https://www.arbeitnow.com/blog/job-board-api  
- JobUp collector / validation — repo `jobup`, VALIDATION_REPORT  
- ADEM open data — https://data.public.lu/en/datasets/skills-required-in-adem-job-vacancies/  
- jobs.lu JobWS — https://en.employers.jobs.lu/JobWS.asmx  
- Jooble REST docs — https://help.jooble.org/en/support/solutions/articles/60001448238-rest-api-documentation  
- Ministero Lavoro SPARQL examples — https://www.lavoro.gov.it/strumenti-e-servizi/open-data/pagine/accesso-ai-dati  
- BA Jobsuche OpenAPI — https://jobsuche.api.bund.dev/  
- BA Nutzungsbedingungen — https://www.arbeitsagentur.de/nutzungsbedingungen  
- Job-Room employer API — https://test-api.job-room.ch/api-docs/jobAdvertisements/v1/  
- Personio recruiting OpenAPI — https://github.com/personio/api-docs/blob/master/personio-recruiting-api.yaml  
- Malt APIs (billing only) — https://api.malt.com/  
- ADEM → EURES jobboard — https://adem.public.lu/en/jobboard.html  

*Not legal advice. Confirm each partner’s redistribution / analytics terms before production Compass ingest.*
