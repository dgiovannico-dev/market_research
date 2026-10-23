# GEO research — EU/CH board access paths

**Date:** 2026-10-21  
**Scope:** Official / first-party access for automated job ingest (market research). Web research only.  
**Policy context:** Prefer authorized APIs/feeds; do not scrape HTML of paid boards ([ADR-003](../decisions/ADR-003-authorized-connectors-only.md)). Repo already scaffolds `adzuna`, `jooble`, `bundesagentur` ([CREDENTIALED_CONNECTORS.md](CREDENTIALED_CONNECTORS.md)).

Legend for **access class**:

| Class | Meaning |
|-------|---------|
| **A — Self-serve** | Register / use without sales call |
| **B — Partner / NCO** | Admission, contract, or account manager |
| **C — Write-only** | Employer/ATS push *into* the board (not a read/ingest API) |
| **D — Unofficial** | SPA/backend endpoints documented by third parties; no official ingest licence |
| **E — Dead / N/A** | Brand discontinued or no usable product |

---

## 1. EURES (EU job mobility)

| | |
|--|--|
| **Access class** | **B** (official) · **D** (portal SPA, unofficial) |
| **Official portal** | https://eures.europa.eu/ |
| **Become Member/Partner** | https://eures.europa.eu/eures-services/how-become-eures-partner-member_en |
| **Legal basis (APIs for Members/Partners)** | [Commission Implementing Decision (EU) 2017/1257](https://eur-lex.europa.eu/eli/dec_impl/2017/1257/oj/eng) — ECO makes vacancies available via application interfaces to admitted EURES Members/Partners; specs live on the **EURES Extranet**, not the public web |
| **Open data / public job API?** | **No** published official public job-search API or bulk open-data dump for third-party aggregators |
| **Statistics** | https://eures.europa.eu/eures-services/eures-portal-statistics_en (visualisations; not a vacancy dump) |
| **Signup path** | National admission via each country’s National Coordination Office (NCO); must provide at least one of: vacancy transmission, CV pool, support services. Not a developer self-serve key |
| **Free tier** | Network participation is a regulatory/PES partnership track, not a freemium developer product |
| **Rate limits** | Not publicly documented for third parties |
| **ToS / aggregation** | Portal end-user use ≠ bulk market-research licence. Official reuse is through Member/Partner admission and Extranet specs. Community reverse-engineered OpenAPI ([rorar/EURES-API-Documentation](https://github.com/rorar/EURES-API-Documentation), base `https://europa.eu/eures/api`) documents SPA calls such as `POST .../jv-searchengine/public/jv-search/search` — **unofficial, unstable, not an authorized connector path** |
| **Repo note** | Catalog: `partner_api` / `NEEDS_CREDENTIALS` — correct |

**Verdict:** Not implementable without national EURES admission (multi-month, employment-services obligations). Do not build on the unofficial SPA API for production ingest.

---

## 2. German BA / Bundesagentur (Jobsuche)

| | |
|--|--|
| **Access class** | **A/D** (SPA client key, community-documented) · **B/C** (official HR-BA-XML = employer *write*) |
| **Community / bund.dev docs** | https://jobsuche.api.bund.dev/ · https://github.com/bundesAPI/jobsuche-api |
| **Host** | `https://rest.arbeitsagentur.de/jobboerse/jobsuche-service` |
| **Search** | `GET /pc/v6/jobs` with header `X-API-Key: jobboerse-jobsuche` (public **clientId**, not a partner-issued secret) |
| **Details** | `GET /pc/v4/jobdetails/{base64(referenznummer)}` |
| **Official partner write path** | [HR-BA-XML](https://www.arbeitsagentur.de/unternehmen/arbeitskraefte/hr-ba-xml-schnittstelle) — employer account + **Kooperationsvereinbarung** + client cert; pushes vacancies *to* BA |
| **Signup for read?** | None. The key is the fixed public client id used by the Jobsuche web/app clients |
| **Free tier** | No billing for the public client id; not an SLA’d open-data product |
| **Rate limits** | Not officially published; treat as soft/unknown — throttle aggressively |
| **ToS / aggregation** | [Nutzungsbedingungen](https://www.arbeitsagentur.de/nutzungsbedingungen) §2a(3): forbid robots/web spiders **and** using existing APIs *contrary to the BA’s intended purpose* to collect/evaluate data. Market-research aggregation is therefore **legally grey / likely disallowed** without written BA permission, even though the endpoint answers anonymously |
| **Repo note** | Connector uses `BUNDESAGENTUR_API_KEY` → set to `jobboerse-jobsuche` for probes; keep catalog `NEEDS_CREDENTIALS` until live promote + legal OK |

**Verdict:** Technically P0 (no sales). **Do not treat as cleared for production market research** until legal review or BA written reuse terms. Official “partner” track is write-side XML, not a read feed.

---

## 3. StepStone / JobStairs (DE/AT/etc.)

### StepStone

| | |
|--|--|
| **Access class** | **C / B** — partner JobFeed for employers/ATS (**inbound** to StepStone) |
| **Docs** | https://api.stepstone.com/ · [Feed types](https://api.stepstone.com/feed-types/) · [XML guide](https://api.stepstone.com/stepstone-xml-guide/) · [Push](https://api.stepstone.com/knowledge-base/push/) |
| **Endpoint (push)** | `https://jobfeed.stepstone.com/listing/` (customer username/pwd) |
| **Signup** | [Jobfeed questionnaire](https://api.stepstone.com/jobfeed-questionnaire/) — requires StepStone **customer number** (CN-…) |
| **Free tier** | No public free read API |
| **Read/ingest API?** | **No** documented public API to pull StepStone’s inventory for aggregation |
| **ToS** | Contractual customer feed; aggregation of StepStone’s board is partner/commercial only |

### JobStairs

| | |
|--|--|
| **Access class** | **B / C** — employer partnership (Partner Fee); HR-XML/JSON **into** JobStairs |
| **Partner site** | https://www.jobstairs-partner.de/ · contact `info@jobstairs.de` |
| **Read/ingest API?** | **No** public third-party read feed |

**Verdict:** Partner-only for posting. **Not** a P0 ingest source without enterprise/customer relationship.

---

## 4. Switzerland — jobs.ch / JobCloud / JobRoom

### JobCloud / jobs.ch (commercial)

| | |
|--|--|
| **Access class** | **C** — advertiser XML / crawler **to publish on** jobs.ch |
| **Docs** | https://www.jobcloud.ch/c/en/technical-solution/ · [XML specs](https://www.jobcloud.ch/c/en/technical-solution/xml-fields/) |
| **Read/ingest API?** | **No** public jobs search API for third parties |
| **Signup** | JobCloud commercial / customer integration |

### Job-Room (SECO / arbeit.swiss — public employment)

| | |
|--|--|
| **Access class** | **C / B** official Jobs API (employer **publish**) · **D** SPA search used by the public UI |
| **Official Jobs API (write)** | Docs: https://test-api.job-room.ch/api-docs/jobAdvertisements/v1/index.html · Prod: `https://api.job-room.ch/jobAdvertisements/v1` · Request credentials: `jobroom-api@seco.admin.ch` (subject “Job-Room API access”) |
| **Purpose** | Employers comply with Stellenmeldepflicht / publish to PES — **not** a bulk download product |
| **Public SPA search (observed)** | `POST https://www.job-room.ch/jobadservice/api/jobAdvertisements/_search` — used by the Angular UI; **no official OpenAPI for third-party aggregators** |
| **Legal** | [Rechtliche Hinweise](https://www.arbeit.swiss/de/rechtliche-hinweise): copyright on contents and open Stellen; reproduction / integration requires **prior written consent** of rights holders |
| **Free tier** | Employer Jobs API access is credentialed by SECO (not a freemium developer portal). SPA has no signup but is not licensed for bulk reuse |
| **Rate limits** | Official API: per agreement. SPA: unknown; datacenter IPs often blocked (third-party reports) |

**Verdict:** No clean self-serve **read** licence. Official API is write-side. SPA search is D-class — incompatible with ADR-003 without SECO written permission.

---

## 5. Luxembourg — jobs.lu / Monster LU / Moovijob

### jobs.lu

| | |
|--|--|
| **Access class** | **B** (SOAP with `key`) |
| **WSDL / ops** | https://en.employers.jobs.lu/JobWS.asmx · `SearchJobs` includes required `<key>` |
| **Signup** | Employer area https://en.employers.jobs.lu/Client/Login — **no** public self-serve developer signup found |
| **Free tier** | Not documented as free public API |
| **ToS** | Employer/client terms; treat SearchJobs as partner-keyed |

### Monster Luxembourg

| | |
|--|--|
| **Access class** | **B** |
| **Site** | https://career-services.monster.lu/ (and Monster.lu) |
| **Read API** | Monster Job Search API (`api.jobs.com`) requires **AppId/AppSecret from Monster** — not self-serve; Media Alliance / account manager for feeds |
| **Free tier** | No |

### Moovijob

| | |
|--|--|
| **Access class** | **B / C** (they syndicate *outbound* to media partners) |
| **Partners page** | https://en.moovijob.com/partners |
| **Public ingest API?** | **No** documented API for third parties to pull Moovijob inventory |

**LU P0-adjacent (not a board partnership):** [Techmap](https://techmap.io/pricing) advertises a **free Luxembourg job dataset** via AWS Data Exchange (~historical + ongoing LU exports). That is a data-vendor path, not jobs.lu/Moovijob official access — evaluate separately if LU coverage is urgent.

**Verdict:** Board-native LU APIs are partner/employer gated. No realistic no-sales board ingest.

---

## 6. Italy — Subito Lavoro / CornerJob / Talent.com

### Subito Lavoro (subito.it)

| | |
|--|--|
| **Access class** | **E / scrape-only** for third parties |
| **Official public job feed/API?** | **None found** |
| **ToS** | Classifieds ToS; third-party Apify scrapers exist — **out of policy** for this repo |

### CornerJob

| | |
|--|--|
| **Access class** | **E** |
| **Status** | Acquired by Eurofirms Group (2019); consumer marketplace brand discontinued. **No** current public API |

### Talent.com (incl. Italy)

| | |
|--|--|
| **Access class** | **B** — publisher program |
| **Publishers** | https://employers.talent.com/publishers · help: publishers form / `publishers@talent.com` ([helpcenter](https://helpcenter.talent.com/hc/en-us/sections/49968625208212-Enterprise-integrations)) |
| **Products** | XML feeds, “self-serve Job API”, affiliate URLs — aimed at **job boards monetizing traffic**, not free research dumps |
| **Employer XML (write into Talent)** | https://www.talent.com/integrations (ATS → Talent) |
| **Free tier** | Not a documented free research quota; contact publishers team |
| **ToS** | Publisher/affiliate agreement; commercial use under their program |

**Italy adjacent (not in the numbered ask, but self-serve-ish):** [Careerjet Italy publisher API](https://www.careerjet.it/partners/api) — Basic Auth with publisher key; requires publisher account + `user_ip` / `user_agent` per call (affiliate-style).

**Verdict:** No free public IT feed among Subito / CornerJob / Talent. Talent.com is sales/publisher contact; CornerJob is dead; Subito is scrape-only.

---

## 7. Jooble / Adzuna (multi-country) — already partial in repo

### Adzuna

| | |
|--|--|
| **Access class** | **A** (keys) · licence **B** for ongoing commercial/org research |
| **Docs** | https://developer.adzuna.com/overview · search: https://developer.adzuna.com/docs/search |
| **ToS** | https://developer.adzuna.com/docs/terms_of_service |
| **Signup** | Register at developer.adzuna.com → immediate `app_id` + `app_key` |
| **Free tier** | Yes — evaluate; no payment card required. Limits shown in account; commonly cited defaults ~25/min, 250/day, 2 500/month (confirm in dashboard) |
| **EU/CH countries (path codes)** | Includes at least `de`, `at`, `ch`, `it`, `fr`, `nl`, `be`, `pl`, `es`, … (same `/jobs/{country}/search/{page}` shape) |
| **Commercial / market research** | Personal & academic research allowed with attribution. **Commercial, government, or academic organisations:** 14-day trial for coverage/usability testing only — **may not use aggregation (counts, average salaries, etc.) for ongoing research** without written consent; revenue/lead products need a licence. Contact Adzuna after trial |
| **Repo** | `ADZUNA_APP_ID` / `ADZUNA_APP_KEY` · connector `adzuna` |

### Jooble

| | |
|--|--|
| **Access class** | **A** (per-country key) · paid/partner for volume |
| **Docs** | https://help.jooble.org/en/support/solutions/articles/60001448238-rest-api-documentation · connect: https://help.jooble.org/en/support/solutions/articles/60000922689-how-to-connect-to-the-jooble-rest-api |
| **Signup** | Per country: e.g. https://de.jooble.org/api/about , https://it.jooble.org/api/about , https://ch.jooble.org/api/about — each domain’s key is **country-scoped** |
| **Free tier** | Yes — **500 requests lifetime per key** (absolute, not monthly) |
| **Rate limits** | Lifetime quota is the hard free limit; HTTP 403 on bad key |
| **ToS** | Jooble API Terms of Use (linked from help center) — comply for any redistribution |
| **Repo** | `JOOBLE_API_KEY` · connector `jooble` — insufficient alone for continuous multi-country ingest |

---

## P0 — realistically implementable without enterprise sales

Ordered by “can start this week” vs legal/quota caveats.

| Priority | Source | Why P0 | Blocker / action |
|----------|--------|--------|------------------|
| **P0-1** | **Adzuna** | Self-serve keys; multi-country incl. DE/AT/CH/IT/FR/…; connector already in repo | For **ongoing commercial market research / KPIs**, email Adzuna for a **written licence** before relying on aggregates past the 14-day org trial ([ToS](https://developer.adzuna.com/docs/terms_of_service)). Stay inside free/personal–academic limits until then |
| **P0-2** | **Jooble** | Self-serve per-country keys; connector exists | Free = **500 lifetime** calls/key → use for validation / thin samples only; ask Jooble support for higher quota (may still be lightweight sales, not “enterprise StepStone”) |
| **P0-3** | **BA Jobsuche** (`X-API-Key: jobboerse-jobsuche`) | No partner signup; richest DE PES inventory; connector ready | **Legal:** Nutzungsbedingungen appear to forbid API use for Datensammlung/-auswertung. Get written BA clarification **or** keep disabled in production. Throttle hard |
| **P0-4** | **Existing PES already in product** (out of list but same GEO) | France Travail OAuth, Reed RSS, ATS tenants, etc. | Prefer these over D-class SPA boards |

### Explicitly **not** P0 (need sales / NCO / write-only / dead)

- EURES official APIs (Member/Partner + Extranet)  
- StepStone JobFeed / JobStairs (inbound partner)  
- JobCloud jobs.ch read  
- Job-Room official API (write) or SPA scrape  
- jobs.lu SOAP key, Monster LU, Moovijob pull  
- Subito Lavoro, CornerJob, Talent.com publishers (contact / dead / scrape)

### Optional LU stopgap (vendor, not board)

- Techmap free LU dataset (AWS Data Exchange) if Luxembourg volume matters before any board partnership.

---

## Recommended next actions (ops, not code)

1. Register Adzuna; set env; run DE/CH/IT country slices; calendar the **org trial / licence** conversation if product is commercial research.  
2. Register Jooble keys for target EU domains; expect quota exhaustion — document as sample-only.  
3. Legal note on BA Jobsuche before promoting `bundesagentur` to ACTIVE for aggregation.  
4. Do **not** schedule unofficial EURES / Job-Room SPA / Subito scrapers.  
5. If DE commercial board coverage is mandatory → start StepStone/JobCloud **BD**, not engineering.

---

## Sources (primary)

- EURES Member/Partner: https://eures.europa.eu/eures-services/how-become-eures-partner-member_en  
- EUR-Lex 2017/1257: https://eur-lex.europa.eu/eli/dec_impl/2017/1257/oj/eng  
- BA Nutzungsbedingungen: https://www.arbeitsagentur.de/nutzungsbedingungen  
- BA HR-BA-XML: https://www.arbeitsagentur.de/unternehmen/arbeitskraefte/hr-ba-xml-schnittstelle  
- bund.dev Jobsuche: https://jobsuche.api.bund.dev/  
- StepStone API: https://api.stepstone.com/  
- JobCloud technical: https://www.jobcloud.ch/c/en/technical-solution/  
- Job-Room Jobs API: https://test-api.job-room.ch/api-docs/jobAdvertisements/v1/index.html  
- arbeit.swiss legal: https://www.arbeit.swiss/de/rechtliche-hinweise  
- jobs.lu JobWS: https://en.employers.jobs.lu/JobWS.asmx  
- Talent publishers: https://employers.talent.com/publishers  
- Adzuna ToS: https://developer.adzuna.com/docs/terms_of_service  
- Jooble REST docs: https://help.jooble.org/en/support/solutions/articles/60001448238-rest-api-documentation  
