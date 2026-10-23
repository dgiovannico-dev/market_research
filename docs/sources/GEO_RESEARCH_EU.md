# EU geographic source research (beyond IT / CH / LU / DE)

Research date: **2026-10-21**. Scope: legal / authorized job data for France, Spain, Netherlands, Belgium, Austria, Nordics (SE/NO/DK/FI), Poland, Czechia, Portugal, Ireland, plus EURES / EU-wide.

Aligned with [ADR-003](../decisions/ADR-003-authorized-connectors-only.md): public APIs, documented feeds, or explicit partner credentials only. **No LinkedIn / Indeed scrape.** Undocumented “site XHR” endpoints are noted as gray-zone and ranked below official open data / partner APIs.

## Already in this repo (do not re-discover)

| Connector | Country / scope | Access |
|-----------|-----------------|--------|
| `france_travail` | FR | OAuth2 client credentials (`francetravail.io` Offres v2) — scaffold |
| `arbetsformedlingen` | SE | Public PES API |
| `nav_arbeidsplassen` | NO | Public search API |
| `nav_stilling_feed` | NO | pam-stilling-feed dump (JWT publicToken) |
| `duunitori` | FI | Public JSON API |
| `jobindex` | DK | Public RSS |
| `nofluffjobs` | PL (+ CEE IT) | Public dump / API path |
| `landing_jobs` | PT (+ EU tech) | Public API |
| `adzuna` | Multi (incl. FR, ES, NL, BE, AT, PL, …) | App id/key — scaffold |
| `jooble` | Multi | API key — scaffold |
| ATS boards | Employer-scoped | Public board APIs |

Gaps called out in [COVERAGE_GAPS.md](COVERAGE_GAPS.md): BE / NL PES, official FI/DK PES, IE official API, EURES partner path. Iberia IT covered by `tecnoempleo` (ES) + `okemprego`/`landing_jobs` (PT).

---

## Priority legend

| Tier | Meaning |
|------|---------|
| **P0** | Documented official open data / free partner API / high-IT documented feed; clear ToS path; fills a real geo gap |
| **P1** | Documented but needs partnership, keys, or commercial licence; or secondary IT board |
| **P2** | Thin IT, outbound-only APIs, aggregated stats (not listings), or gray-zone undocumented endpoints |

**IT density** (for this product): High = tech roles common / specialised IT board; Medium = general PES with some IT; Low = mostly non-IT / sparse tech.

---

## Top ranked list (integration order)

| Rank | Source | Country | Mode | Auth | IT dens. | Pri | One-line why |
|------|--------|---------|------|------|----------|-----|--------------|
| 1 | **MPSV / ÚP ČR open vacancies** | CZ | Open data JSON dump (daily) | None | Medium | **P0** | Official free full-country dump; no scrape |
| 2 | **Le Forem Open Data (ODWB)** | BE-WA | Open data REST | None (ODS) | Medium | **P0** | Official Wallonia listings as open data |
| 3 | **Tecnoempleo RSS** (+ partner API) | ES | Documented RSS; partner XML/JSON | None / contact | **High** | **P0** | Best legal Spain IT feed without InfoJobs scrape |
| 4 | **Poland ePraca (CBOP) WebService** | PL | Official SOAP → ZIP/JSON | Signed terms + subject id | Medium | **P0** | Free MRPiPS integrator API; complements NoFluffJobs |
| 5 | **Työmarkkinatori job retrieval API** | FI | Documented partner REST (KIPA P67) | KEHA activation + API key | Medium | **P0** | Official FI PES beyond Duunitori |
| 6 | **Jobnet JobannonceService (STAR)** | DK | Official SOAP/HR-XML partner | STAR agreement + IP/auth | Medium | **P0** | Official DK PES; prefer over undocumented BFF |
| 7 | **Adzuna country endpoints** | FR/ES/NL/BE/AT/PL | Documented REST aggregator | `app_id` + `app_key` | Medium–High | **P0** | Scaffold exists; expand country codes when keyed |
| 8 | **France Travail Offres v2** | FR | Documented OAuth API | Client id/secret + subscription | Medium–High | **P0** | Activate existing scaffold |
| 9 | **VDAB Vacature API** | BE-VL | Documented partner REST | Partnership + Client-Id + OAuth | Medium | **P1** | Flanders PES; onboarding / agreement required |
| 10 | **Tecnoempleo jobs API** | ES | Partner XML/JSON | Email / commercial | **High** | **P1** | Richer than RSS when granted |
| 11 | **STAR Jobnet webservice (full)** | DK | Partner Job-In/Out | Agreement | Medium | **P1** | Same org as #6; richer sync |
| 12 | **EURES partner JV API** | EU-wide | Partner API (network) | EURES NCO recognition | Medium | **P1** | Portal ToS forbids non-partner extraction |
| 13 | **Actiris search JSON** | BE-BRU | Undocumented public XHR | None observed | Medium | **P2** | Gray-zone; seek partnership first |
| 14 | **JobsIreland BrowseJobs** | IE | Undocumented search endpoint | None observed | Medium | **P2** | Gray-zone; no official integrator docs |
| 15 | **Empléate / SEPE** | ES | No official vacancy API | — | Medium | **P2** | Open data = contracts/stats, not offers; Solr = scrape |
| 16 | **UWV Werk.nl** | NL | No vacancy API | — | Medium | **P2** | Aggregated Open Match only; no listing API |
| 17 | **AMS alle jobs / HR-API** | AT | HR-API = **post** to AMS | eAMS token (employers) | Medium | **P2** | No public pull API documented |
| 18 | **APEC** | FR | ATS publish (ADEP) / XML export partnership | Recruiter / partner | High (cadres) | **P2** | Outbound for employers; no public pull for us |
| 19 | **IEFP Online** | PT | No documented API | — | Low–Medium | **P2** | Landing.jobs already covers PT tech |
| 20 | **InfoJobs / Pracuj.pl / Jobs.cz** | ES/PL/CZ | Commercial partner only | Paid / ATS deals | High | **P2** | Catalogued; no scrape; pursue licence later |

---

## Source cards

### EU-wide

#### EURES (European Employment Services)

| Field | Detail |
|-------|--------|
| Country | EU / EEA (+ partners); portal shows 30+ countries |
| URL | https://eures.europa.eu/ · Find a job: https://europa.eu/eures/portal/jv-se/home |
| Access mode | **Partner API** (official). Portal search UI is for end users. Community OpenAPI exists but is **unofficial**. |
| Auth | Recognised EURES partner via National Coordination Office; formats/standards via EURES Extranet |
| IT density | Medium (general labour; tech present) |
| Priority | **P1** (strategic EU coverage) / **REJECT** for anonymous portal scraping |
| ToS notes | Portal ToS: no screen scraping / automated extraction to re-publish; **only EURES partner organisations** may extract via API. Legal base: Commission Implementing Decision (EU) 2017/1257 (Member ↔ portal channels). |
| Repo | Catalog `EURES` = `NEEDS_CREDENTIALS` / `partner_api` |

#### Adzuna (multi-country)

| Field | Detail |
|-------|--------|
| Country | Among others: **at, be, es, fr, nl, pl** (+ de/it/ch/gb/…); **not** IE/PT in common SDK country lists |
| URL | https://developer.adzuna.com/ |
| Access mode | Documented REST aggregator |
| Auth | Free registration → `app_id` + `app_key` (query params); commercial licence for ongoing republish |
| IT density | Medium–High (filterable; IT categories) |
| Priority | **P0** (keys + live promote) |
| ToS notes | Developer terms; publishing listings / commercial use may need paid licence — verify before production republish. |
| Repo | Connector `adzuna` scaffolded |

---

### France

#### France Travail — Offres d'emploi

| Field | Detail |
|-------|--------|
| Country | FR |
| URL | https://francetravail.io/ · https://www.francetravail.fr/ |
| Access mode | Documented OAuth2 API (Offres v2) |
| Auth | Client credentials; app + subscription on francetravail.io |
| IT density | Medium–High |
| Priority | **P0** — activate existing `france_travail` |
| ToS notes | Distribution / reuse rules can change; confirm current Emploi Store terms before production. |

#### APEC

| Field | Detail |
|-------|--------|
| Country | FR (cadres / executives) |
| URL | https://www.apec.fr/ |
| Access mode | **Partner / ATS publish** (API ADEP since 2026-01-28); XML export partnership for selected partners |
| Auth | Recruiter account / ATS partner — **not a public pull API** |
| IT density | High among cadres (IT management / engineering) |
| Priority | **P2** for our ingest model |
| ToS notes | Designed to push offers *to* Apec, not bulk-pull for a third-party intelligence product. Export via standardised XML requires partnership request. |

---

### Spain

#### Tecnoempleo

| Field | Detail |
|-------|--------|
| Country | ES (IT / telecom specialty) |
| URL | https://www.tecnoempleo.com/ · RSS help: `/ofertas-empleo-rss.php` · Partner API: `/api-integraciones.php` |
| Access mode | **Documented RSS** after search / alert; **partner XML/JSON API** on request (`info@tecnoempleo.com`) |
| Auth | RSS: none; API: commercial / partner |
| IT density | **High** |
| Priority | **P0** (RSS first), **P1** (full API) |
| ToS notes | RSS presented as intentional syndication for candidates/sites. Partner API for showing offers on third-party sites — get written terms for analytics/republish scope. |

#### Empléate / SEPE

| Field | Detail |
|-------|--------|
| Country | ES |
| URL | https://empleate.gob.es · SEPE open data: https://sede.sepe.gob.es/…/catalogo-de-datos-del-SEPE |
| Access mode | Portal search only. Open data = **contracts / demandantes / spend**, not vacancy listings. Third parties reverse-engineer Solr — **not official**. |
| Auth | N/A for listings API |
| IT density | Medium |
| Priority | **P2** / treat Solr as **unsupported scrape** under ADR-003 |
| ToS notes | Prefer Tecnoempleo + Adzuna `es` + ATS until SEPE publishes a vacancy API. |

#### InfoJobs

| Field | Detail |
|-------|--------|
| Country | ES |
| URL | https://www.infojobs.net/ |
| Access mode | Commercial / publisher partnership only |
| Auth | Partner credentials |
| IT density | High (general board with large IT) |
| Priority | **P2** until licensed |
| ToS notes | Catalogued; **no scrape**. |

---

### Netherlands

#### UWV Werk.nl

| Field | Detail |
|-------|--------|
| Country | NL |
| URL | https://www.werk.nl/ · Open Match: https://data.overheid.nl/en/dataset/uwv-open-match-data |
| Access mode | **No official vacancy listing API** (data.overheid.nl request #2258: UWV stated no API; “scraping possible” historically — **not** an authorized connector path for us). Open Match = **aggregated** vacancy/CV counts by occupation × 4-digit postcode (CC-BY). |
| Auth | None for aggregates |
| IT density | Medium (aggregates only) |
| Priority | **P2** for aggregates; listings **BLOCKED** without new official API |
| ToS notes | Prefer Adzuna `nl` + ATS tenants for NL IT demand signals. See [NL_JOBS_COVERAGE.md](NL_JOBS_COVERAGE.md). |

#### findmethatdamjob.nl (public API)

| Field | Detail |
|-------|--------|
| Country | NL |
| URL | https://findmethatdamjob.nl/ · API https://gigsignal-api.fly.dev/api/jobs |
| Access mode | **Documented public read API** (no auth; 30m cache; fair-use User-Agent) |
| Auth | None |
| IT density | Medium–High (Amsterdam / NL tech employers from careers pages) |
| Priority | **P0** (free NL listing path; not a PES substitute) |
| ToS notes | Listings sourced from employer career pages; respect source employers on republish. |
| Connector | **`findmethatdamjob`** — `GET /api/jobs?location=amsterdam` (NL-wide per docs) |

---

### Belgium

#### Le Forem (Wallonia)

| Field | Detail |
|-------|--------|
| Country | BE (Wallonia) |
| URL | Open data: https://www.leforem.be/open-data.html · Dataset: https://www.odwb.be/explore/dataset/offres-d-emploi-forem/ · Partner HR-XML APIs: https://www.leforem.be/api/flux-offres/ |
| Access mode | **Open data** (ODWB, free, near-real-time summaries) **and** partner HR-XML APIs (publish / exchange with codes) |
| Auth | Open data: none; Partner APIs: request + access codes (CGU PDF) |
| IT density | Medium |
| Priority | **P0** (ODWB), **P1** (full partner APIs) |
| ToS notes | Open data for reuse under regional open-data decree; contacts/applications still via Forem site. Partner APIs: recruitment purpose; no credential sharing. |
| Connector | **`le_forem`** (dump) — ODWB Explore `GET /api/explore/v2.1/catalog/datasets/offres-d-emploi-forem/records` (limit/offset, cap 200). No key. Partner HR-XML / VDAB not used. |

#### VDAB (Flanders)

| Field | Detail |
|-------|--------|
| Country | BE (Flanders) |
| URL | https://developer.vdab.be/ · Vacature product; Extranet CoE docs |
| Access mode | Documented REST Vacature API (v4.x): search, bulk, by id |
| Auth | **Not open data**: partnership + cooperation agreement; `X-IBM-Client-Id` + OAuth2/OIDC. Open-data portal is for competency/reference data, not vacancies. |
| IT density | Medium |
| Priority | **P1** |
| ToS notes | Vacancy API for professional use with mutual value; new applications may be temporarily paused — check CoE page. |

#### Actiris (Brussels)

| Field | Detail |
|-------|--------|
| Country | BE (Brussels-Capital) |
| URL | https://www.actiris.brussels/ |
| Access mode | Public website; third parties use undocumented JSON search API. **No official integrator documentation found.** |
| Auth | None observed on public search |
| IT density | Medium (notable IT sector filters on site) |
| Priority | **P2** until partnership / docs |
| ToS notes | Under ADR-003, do not treat undocumented XHR as authorized. Contact Actiris for a feed/API agreement. |

---

### Austria

#### AMS (Arbeitsmarktservice)

| Field | Detail |
|-------|--------|
| Country | AT |
| URL | https://www.ams.at/allejobs · HR-API: https://www.ams.at/unternehmen/…/ams-hr-api |
| Access mode | **HR-API = employer → AMS posting** (eAMS token). Public “alle jobs” search has **no documented pull API**. |
| Auth | eAMS Konto + HR-API token (employers / ATS vendors) |
| IT density | Medium |
| Priority | **P2** for pull ingest |
| ToS notes | Help pages describe crawler-sourced internet jobs inside “alle jobs”; that does not grant third parties scrape rights. Prefer Adzuna `at` + ATS. |

---

### Nordics

#### Sweden — Arbetsförmedlingen

| Field | Detail |
|-------|--------|
| Status | **Already integrated** (`arbetsformedlingen`) |
| Priority | Maintain |

#### Norway — NAV Arbeidsplassen

| Field | Detail |
|-------|--------|
| Status | **Already integrated** (`nav_arbeidsplassen`) |
| Priority | Maintain |

#### Finland — Työmarkkinatori (Job Market Finland / ex TE-palvelut)

| Field | Detail |
|-------|--------|
| Country | FI |
| URL | https://tyomarkkinatori.fi/en/instructions-and-support/interfaces/interfaces-for-job-postings · Tech: KIPA P67 `POST https://api.ahtp.fi/kipa/p67/v2/jobpostings` |
| Access mode | Documented **retrieval** + import APIs |
| Auth | KEHA Centre activation form + terms; business ID–linked credentials; `KIPA-Subscription-Key`; NDJSON stream |
| IT density | Medium |
| Priority | **P0** (official PES; Duunitori remains commercial board) |
| ToS notes | Commit to KEHA terms of use; test then production credentials. Contact: tmt-rajapinnat.keha@ely-keskus.fi |

#### Finland — Duunitori

| Field | Detail |
|-------|--------|
| Status | **Already integrated** (`duunitori`) |
| Priority | Maintain |

#### Denmark — Jobnet (STAR)

| Field | Detail |
|-------|--------|
| Country | DK |
| URL | https://jobnet.dk/ · Official WS: https://www.star.dk/…/jobnet-webservice · STAR wiki JobannonceService |
| Access mode | Official **SOAP/HR-XML** JobannonceService (import/export) for agreed organisations. Portal also exposes an undocumented `jobnet.dk/bff` used by the site (community tools; **not** first-party docs). |
| Auth | Free WS after STAR agreement; IP allowlist + credentials for sensitive services |
| IT density | Medium |
| Priority | **P0** official WS; **REJECT** relying solely on undocumented BFF |
| ToS notes | Job-Out returns publicly visible ads but still requires agreement. Prefer Jobindex RSS (already live) for quick DK IT until WS onboarded. |

#### Denmark — Jobindex

| Field | Detail |
|-------|--------|
| Status | **Already integrated** (`jobindex` RSS) |
| Priority | Maintain |

---

### Poland

#### ePraca / CBOP (MRPiPS)

| Field | Detail |
|-------|--------|
| Country | PL |
| URL | https://oferty.praca.gov.pl/ · Integrators: https://psz.praca.gov.pl/dla-integratorow · WSDL v2: `https://oferty.praca.gov.pl/integration/services/v2/oferta?wsdl` |
| Access mode | Official SOAP WebService → ZIP of JSON offers |
| Auth | Sign “Warunki udostępniania…” (trusted/qualified e-sign) → email **apicbop@praca.gov.pl** → assigned `podmiot` name. Free. |
| Windows | Downloads **17:00–07:00**; snapshot ~16:00; **≤20 calls / night cycle** |
| IT density | Medium (PES mix; use with NoFluffJobs for IT) |
| Priority | **P0** |
| ToS notes | Do not alter offer text; do not publish stale offers; display **ePraca logo**; lawful use. Legal basis updated 2025 market-services act (see Warunki PDF). |

#### NoFluffJobs

| Field | Detail |
|-------|--------|
| Status | **Already integrated** (`nofluffjobs`) — high IT / B2B |
| Priority | Maintain |

#### Pracuj.pl

| Field | Detail |
|-------|--------|
| Access | Commercial partner / ATS only |
| Priority | **P2** — no scrape |

---

### Czechia

#### MPSV / Úřad práce — Volná místa (open data)

| Field | Detail |
|-------|--------|
| Country | CZ |
| URL | Dataset page: https://data.mpsv.cz/web/data/volna-mista-za-celou-cr · File: https://data.mpsv.cz/od/soubory/volna-mista/volna-mista.json (404 as of 2026-10-21) · Live twin: https://data.mpsv.cz/od/soubory/volna-mista/volna-mista.jsonld (~180MB) · Schema: `volna-mista.schema.json` |
| Access mode | **Official open data** dump, updated daily; vacancies approved for JPŘ PSV portal. Connector `mpsv` streams JSON-LD when compact JSON is missing. |
| Auth | None |
| IT density | Medium (filter by CZ-ISCO / keywords post-ingest) |
| Priority | **P0** |
| ToS notes | Some employers suppress identity/location (`ZverejnovatVpm`); export omits those fields — candidates must contact ÚP. Only published, approved, open positions with count > 0. |

#### Jobs.cz (Alma Career)

| Field | Detail |
|-------|--------|
| Country | CZ |
| URL | https://www.jobs.cz/ |
| Access mode | Paid Alma Career XML export/import for ATS; robots.txt **Disallow: /api/** |
| Auth | Commercial credentials |
| IT density | High |
| Priority | **P2** — licence later; **no scrape** |

---

### Portugal

#### Landing.jobs

| Field | Detail |
|-------|--------|
| Status | **Already integrated** (`landing_jobs`) — strong EUR tech bands |
| Priority | Maintain |

#### okemprego

| Field | Detail |
|-------|--------|
| Status | **ACTIVE** (`okemprego`) — free public API, default PT `it-data` |
| URL | https://www.okemprego.com/pt/api |
| Access mode | Documented JSON API (no key); cite canonical listing URL |
| Auth | None |
| IT density | High (category filter) |
| Priority | Maintain — complements Landing.jobs; optional `OKEMPREGO_COUNTRIES` for BR/AO |
| Evidence | Live insert 148 PT jobs (run 225, 2026-10-21) — [VALIDATION_REPORT](VALIDATION_REPORT.md) |

#### IEFP Online

| Field | Detail |
|-------|--------|
| Country | PT |
| URL | https://iefponline.iefp.pt/ |
| Access mode | Public HTML search; **no documented API / open data vacancy dump found** |
| Auth | N/A |
| IT density | Low–Medium |
| Priority | **P2** — scrape-only community scripts exist; skip under ADR-003 |

---

### Ireland

#### JobsIreland (DSP / Intreo)

| Field | Detail |
|-------|--------|
| Country | IE |
| URL | https://jobsireland.ie/ · gov.ie service page |
| Access mode | Public BrowseJobs UI; path `Jobsireland.API/JobsIreland/BrowseJobs` appears in site. **No official integrator API documentation** found. |
| Auth | None for public browse |
| IT density | Medium |
| Priority | **P2** until DSP publishes terms/API |
| ToS notes | Check JobsIreland Terms before any automation; prefer Adzuna if/when IE is added, or ATS + remote boards for IE tech. |

---

## Recommended next actions (engineering)

1. **P0 dump/API connectors (no commercial negotiation):** MPSV CZ JSON · Le Forem ODWB · Tecnoempleo RSS.
2. **P0 keyed / signed:** Activate `france_travail` + expand `adzuna` country codes (`fr`,`es`,`nl`,`be`,`at`,`pl`); file ePraca Warunki; apply KEHA Työmarkkinatori retrieval; apply STAR Jobnet JobannonceService.
3. **P1 partnerships:** VDAB Vacature; Tecnoempleo JSON API; EURES NCO if product needs pan-EU official feed.
4. **Do not build:** LinkedIn/Indeed scrape; Empléate Solr scrapers; Werk.nl HTML scrapers; Jobs.cz/InfoJobs/Pracuj HTML; EURES anonymous portal harvest; Jobnet undocumented BFF as sole path; AMS alle-jobs crawl.

## Coverage after P0 set (target)

| Geo | Primary legal path |
|-----|-------------------|
| FR | France Travail + Adzuna `fr` (+ APEC later if partnership) |
| ES | Tecnoempleo + Adzuna `es` |
| NL | `findmethatdamjob` + DevITJobs `nl` + Adzuna `nl` when keyed (UWV/Werk.nl PES listings blocked) |
| BE | Forem ODWB + VDAB partner + Adzuna `be` |
| AT | Adzuna `at` + ATS |
| SE/NO | Existing PES connectors |
| FI | Duunitori + Työmarkkinatori |
| DK | Jobindex + Jobnet WS |
| PL | NoFluffJobs + ePraca |
| CZ | MPSV open data (+ Jobs.cz licence later) |
| PT | okemprego + Landing.jobs |
| IE | ATS / remote boards until official API |
| EU | EURES partner **or** multi-country Adzuna — not portal scrape |

## Primary citations (owners)

- EURES portal job-search ToS (partner-only API) — europa.eu/eures portal
- EU 2017/1257 — eur-lex.europa.eu
- Adzuna developer overview — developer.adzuna.com
- France Travail developer portal — francetravail.io
- Tecnoempleo RSS / API pages — tecnoempleo.com
- SEPE open data catalogue — sede.sepe.gob.es (no vacancy listings)
- UWV / data.overheid.nl request 2258 + Open Match dataset
- Le Forem open data + ODWB dataset + API CGU PDF
- VDAB developer portal + Extranet Vacature API CoE
- AMS HR-API + alle jobs help
- Työmarkkinatori job posting interfaces + KIPA P67 docs
- STAR Jobnet webservice pages
- MRPiPS ePraca integrator PDFs (instrukcja + warunki) — oferty.praca.gov.pl
- MPSV volná místa methodology — data.mpsv.cz
- APEC ATS / ADEP publish pages — apec.fr

---

*Catalog sync: after choosing connectors, update `data/sources/catalog.json` via `generate_source_catalog.py` and keep statuses honest (`NEEDS_CREDENTIALS` / `PENDING_ACCESS` until live records).*
