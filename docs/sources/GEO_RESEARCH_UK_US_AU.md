# Geo research: United Kingdom · United States · Australia

Legal job-data sources for **IT / tech / remote / contract** market intelligence. Prefer official or public APIs and RSS. **No Indeed/LinkedIn scrape.** Scraping HTML of paid boards is out of policy ([ADR-003](../decisions/ADR-003-authorized-connectors-only.md)).

Research date: **2026-10-21**. Claims cite first-party docs where possible.

## Already in repo (baseline)

| Connector | Geo affinity | Access | Notes |
|-----------|--------------|--------|-------|
| `reed` | UK | Public RSS; optional `REED_API_KEY` JSON | ACTIVE path via RSS |
| `usajobs` | US federal | Keyed (`USAJOBS_API_KEY` + email UA) | Scaffold; ACTIVE after live keyed run |
| `themuse` | Global / US-heavy | Public API | Remote/employer boards |
| `remotive`, `remoteok`, `working_nomads`, `weworkremotely` | Global remote | Public API/RSS | Strong remote IT; not country-native |
| `adzuna` | Config `ADZUNA_COUNTRY` (default `gb`) | `app_id` / `app_key` | Same key works for `us` / `au` paths |
| `jooble` | Per-domain key | POST `/api/{key}` | **One key = one country** (US `jooble.org`, UK `uk.jooble.org`, AU regional) |
| `devitjobs` | UK / EU IT | Public | Complements Reed for UK tech |

Also relevant (not geo-native): Greenhouse / Lever / Ashby / SmartRecruiters tenant allowlists — good for AU/UK/US employers that publish public boards.

## Priority legend

| Pri | Meaning |
|-----|---------|
| **P0** | Ship next: legal, high IT or official PES signal, clear ingest path, fills a real gap |
| **P1** | Strong candidate; needs keys, partner approval, or operational hardening |
| **P2** | Niche, fragile, low IT density, or access-restricted — keep watched |

**IT density** (for market intel): High = mostly tech/contract; Medium = mixed with filterable IT; Low = general labour / public sector.

---

## Top ranked recommendations

1. **Expand Adzuna to `us` + `au`** (same keys; path `/jobs/{country}/search`) — largest legal multi-country lift with zero new vendor. **P0**
2. **Activate USAJOBS** with live keys + `JobCategoryCode=2210` (IT Management) — official US federal IT. **P0**
3. **Reed Jobseeker JSON API** (optional key already wired) — richer salary/contract fields than RSS for UK. **P0**
4. **Jooble AU + US keys** (separate regional registrations) — aggregator breadth; watch **500 lifetime free requests/key**. **P1**
5. **Findwork.dev Jobs API** — self-serve token, developer/remote-heavy; complements Muse/Remotive. **P1**
6. **DWP Find a Job / Jobs & Careers API** — UK national board; catalogue documents keyed search, but host/`api.gov.uk` entry is mid-migration (2026) — treat as **PENDING_ACCESS**. **P1**
7. **CWJobs search RSS** — UK IT-specialist StepStone board; documented RSS UX, but datacenter probes get **403** — validate from allowed egress before building. **P1**
8. **ACT Government Jobs RSS** (+ data.gov.au listing) — only clear AU **official RSS**; low IT volume; Cloudflare challenge from some IPs. **P2**
9. **APS Public Service Gazette (CC BY 4.0 weekly PDFs)** — legal AU federal vacancies; poor machine format; IT sparse. **P2**
10. **NLx Research Hub** — richest US multi-employer feed; governance-board access; requests paused mid-2026 model change. **P2**

**Do not pursue for search ingest:** SEEK (partner GraphQL; explicitly **no programmatic job search**), Dice (employer/partner posting only), EthicalJobs/CareerOne/Jora (post-in feeds only), Indeed/LinkedIn scrape.

---

## United Kingdom

### Candidates

| Source | URL / docs | Mode | Auth | IT density | Pri | Overlap with existing |
|--------|------------|------|------|------------|-----|------------------------|
| **Reed Jobseeker API** | [reed.co.uk/developers/jobseeker](https://www.reed.co.uk/developers/jobseeker) · RSS `https://www.reed.co.uk/jobs/rss` | API + RSS | RSS none; API Basic (key as username, empty password) | High (filter `contract`/`keywords`) | **P0** | **Same as `reed`** — upgrade default path to keyed JSON when `REED_API_KEY` set (already supported) |
| **Adzuna GB** | [developer.adzuna.com](https://developer.adzuna.com/overview) · `/jobs/gb/search/{page}` | API | `app_id` + `app_key` | Medium–High (IT category + `what`) | **P0** | **`adzuna`** (default country) — activate keys |
| **DevITJobs** | In-repo `devitjobs` | Public feed/API | None | High | — | **Already implemented** |
| **Find a Job (DWP) / Jobs & Careers** | Portal [jobs.service.gov.uk](https://www.jobs.service.gov.uk/); catalogue [api.gov.uk/dwp/find-a-job](https://www.api.gov.uk/dwp/find-a-job/) (endpoint host historically `findajob.dwp.gov.uk`); GitHub catalogue issue documents `api_id` + `api_key` on `/api/search` | API (gov) | `api_id` + `api_key`; aimed at cross-government | Medium (broad PES; IT via `q=`) | **P1** | Catalog id 8 `UNDER_REVIEW`; **partial Adzuna overlap** historically (Adzuna operated Find a Job under DWP contract through mid-2026). New in-house service launching 2026 — re-verify endpoint before coding |
| **CWJobs RSS** | [cwjobs.co.uk RSS help](https://www.cwjobs.co.uk/JobSearch/RSSLink.aspx) · pattern `…/JobSearch/RSS.aspx` (+ search query params from UI) | RSS | None (public feed UX) | **High** (IT board) | **P1** | Catalog id 20 `UNDER_REVIEW`. Distinct from Reed/DevITJobs employer mix. **Probe 2026-10-21:** HTTP 403 from this environment — may need allowlisted egress; Totaljobs sister RSS same StepStone stack |
| **Jooble UK** | [uk.jooble.org/api/about](https://uk.jooble.org/api/about) · docs [help.jooble.org REST](https://help.jooble.org/en/support/solutions/articles/60001448238-rest-api-documentation) | API | Per-domain API key | Medium | **P1** | Overlaps Adzuna/Reed aggregation; **new regional key** vs current Jooble key |
| **LMI for All vacancies** | [lmiforall.org.uk vacancies](https://www.lmiforall.org.uk/developers/data-documentation/vacancies-2/) · explorer [api.lmiforall.org.uk](https://api.lmiforall.org.uk/) | API | Historically free; **data updates stopped end-2024; API access through Oct 2025** | Medium (Find a Job mirror) | **Reject / archive** | Dead for new builds; use DWP/Adzuna instead |
| **Civil Service Jobs** | [civilservicejobs.service.gov.uk](https://www.civilservicejobs.service.gov.uk/) | HTML only | — | Medium (gov IT/digital roles) | **P2 / blocked** | Archived data.gov.uk RSS (last useful ~2016). Live site uses browser challenge — **no legal public API**; do not scrape |
| **jobs.ac.uk RSS** | [jobs.ac.uk/feeds/…](https://www.jobs.ac.uk/feeds/type-roles) | RSS (claimed) | None | Medium (HE IT / research computing) | **P2** | **Probe 2026-10-21:** `/feeds/type-roles` → **404**; third-party reports RSS retired 2026. Re-check before any connector |
| **Totaljobs RSS** | [totaljobs.com RSS help](https://www.totaljobs.com/JobSearch/RSSLink.aspx) | RSS | None | Medium | **P2** | Sister of CWJobs; broader than IT. Employer XML API is **post-in only** ([StepStone Totaljobs UK](https://api.stepstone.com/knowledge-base/totaljobs-uk/)) |

### UK notes

- **Highest incremental value:** keyed Reed JSON + live Adzuna GB + (if RSS reachable) CWJobs for contract IT rates.
- **Official PES:** DWP Find a Job API is the right long-term national source; access model is **not self-serve for arbitrary commercial apps** — expect partner/gov process. Catalogue start date listed as Jun 2026; portal domain migrating toward `jobs.service.gov.uk`.

---

## United States

### Candidates

| Source | URL / docs | Mode | Auth | IT density | Pri | Overlap with existing |
|--------|------------|------|------|------------|-----|------------------------|
| **USAJOBS Search API** | [developer.usajobs.gov](https://developer.usajobs.gov/general/quick-start) · `GET https://data.usajobs.gov/api/search` | API | Free key via request form; headers `Host`, `User-Agent` (registered email), `Authorization-Key` | Medium–High for series **2210** / Keyword=`Software` | **P0** | **`usajobs`** — enable env + promote after inserts. Federal only (not private sector) |
| **Adzuna US** | `/jobs/us/search/{page}` | API | Same Adzuna app credentials | Medium–High | **P0** | **`adzuna`** country flip — primary private-sector legal aggregator |
| **Jooble US** | [jooble.org/api/about](https://jooble.org/api/about) | API | US-domain key; **500 lifetime free requests** | Medium | **P1** | Overlaps Adzuna; good secondary aggregator if quota acceptable |
| **Findwork.dev** | [findwork.dev/developers](https://findwork.dev/developers/) · `GET /api/jobs/` | API | Token (`Authorization: Token …`); account signup | **High** (dev jobs, remote filter) | **P1** | Overlaps Remotive/RemoteOK/Muse; smaller board, clean JSON |
| **The Muse / remote boards** | In-repo | API/RSS | None / public | High remote | — | **Already implemented** |
| **NLx / CareerOneStop Jobs** | [nlxresearchhub.org/data-access](https://nlxresearchhub.org/data-access) · CareerOneStop notes jobs moved to NLx | API / files | Data-use agreement; governance board; **request processing paused** (check back Nov 2026 per site) | Medium (employer + state banks) | **P2** | Currently authorized mainly for SWA LMI / discrete nonprofit research — **product integration may be denied**. Do not scrape CareerOneStop |
| **CareerBuilder Job Search API** | [api.careerbuilder.com](https://api.careerbuilder.com/Search/jobsearch/jobsearchinfo.aspx) | API | `DeveloperKey` | Medium | **P2** | Commercial; HostSite=`US`. Overlaps Adzuna/Jooble. Partner/sales path |
| **Dice** | [Dice integrations](https://www.dice.com/support/employer-experience/integration-capabilities--instructions.html) | Partner ATS / batch **posting** | Account team / secret key | **High** tech (if accessible) | **Reject for search** | No public job-search API; employer-side only |
| **FlexJobs** | Employer XML **inbound** | Feed (post) | Partner | High remote/flex | **Reject for search** | Cannot pull marketplace listings |

### US notes

- Private-sector IT coverage gap vs federal: **Adzuna US + Findwork + existing remote boards** is the legal stack.
- USAJOBS is excellent for **gov digital/IT** salary bands and geography — not a proxy for Silicon Valley contractor rates.

---

## Australia

### Candidates

| Source | URL / docs | Mode | Auth | IT density | Pri | Overlap with existing |
|--------|------------|------|------|------------|-----|------------------------|
| **Adzuna AU** | `/jobs/au/search/{page}` · country list includes `au` ([developer.adzuna.com](https://developer.adzuna.com/overview)) | API | Same Adzuna keys | Medium–High | **P0** | **`adzuna`** — **best AU commercial legal path**; fills largest coverage gap |
| **Jooble AU** | Regional Jooble AU domain `/api/about` (per-country key rule) | API | AU-domain key; 500 lifetime free | Medium | **P1** | Overlaps Adzuna AU |
| **ACT Government Jobs RSS** | [jobs.act.gov.au opportunity alerts](https://www.jobs.act.gov.au/how-we-hire/opportunity-alerts); feed pattern `https://www.jobs.act.gov.au/rss/subscribe?…`; listed on [data.gov.au](https://www.data.gov.au/data/dataset?q=vacant+ACT+government+jobs) | RSS | None | Low (territory public sector) | **P2** | No overlap with current collectors. **Probe:** Cloudflare challenge (403) from some IPs — confirm feed stability before connector |
| **APSJobs / Public Service Gazette** | [apsjobs.gov.au](https://apsjobs.gov.au/); weekly vacancy PDFs on APSC S3 (CC BY 4.0 for vacancy text; contact PII excluded) | PDF gazette | None for PDF | Low–Medium (APS digital/IT roles) | **P2** | Legal reuse under CC BY with attribution; **no official JSON API**. Scraping portal HTML discouraged |
| **Workforce Australia** | [workforceaustralia.gov.au](https://www.workforceaustralia.gov.au/individuals/jobs/search) | HTML portal | — | Medium | **Blocked** | No first-party public search API found. Third-party scrapers exist — **out of policy** |
| **SEEK API** | [developer.seek.com](https://developer.seek.com/) · reflecting ads: [“does not offer programmatic job search”](https://developer.seek.com/use-cases/job-posting/reflecting-job-ads) | Partner GraphQL | OAuth partner + hirer relationships | N/A for search | **Reject** | Dominant AU board — **cannot search listings**. Posting/apply only |
| **EthicalJobs / CareerOne / Jora** | Employer XML **post** APIs | Post-in | Partner keys | Medium / niche | **Reject for search** | No public job-search pull |
| **Lake Macquarie Council Jobs RSS** | [data.gov.au dataset](https://data.gov.au/data/dataset/jobs-lake-macquarie-city-council) | RSS | None | Very low | **P2** | Local council only — ignore for national IT intel |

### AU notes

- **SEEK is not a viable search source** under their own docs — plan around Adzuna/Jooble + ATS tenants of AU tech employers.
- Official AU vacancy machine feeds are **thin** (territory/council RSS + APS gazette PDFs). Accept that commercial aggregators carry most private IT signal.

---

## Cross-cutting / remote (already covered)

Keep using existing remote collectors for AU/UK/US remote contract roles: Remotive, Remote OK, We Work Remotely, Working Nomads, The Muse, Jobicy, Himalayas, HN Who’s Hiring. They do **not** replace country-native boards for on-site/hybrid local rates.

---

## Rejected or out of scope

| Source | Reason |
|--------|--------|
| Indeed / LinkedIn | Publisher/partner only; **no scrape** (user request + ADR-003) |
| SEEK search | Official: no programmatic job search |
| Dice / FlexJobs search | No public pull API |
| CWJobs/Totaljobs Apify scrapers | Scrape wrappers — not authorized first-party |
| LMI for All vacancies | Service end-of-life |
| Civil Service Jobs scrape | No API; CAPTCHA |
| Workforce Australia scrape | No API |

---

## Suggested implementation order

1. **Config/ops only:** Set Adzuna keys; run `gb`, then `us`, then `au` search queries for IT keywords; promote ACTIVE when inserts > 0.
2. **Config/ops only:** USAJOBS keys + 2210 / software keyword runs.
3. **Config polish:** Prefer Reed JSON when `REED_API_KEY` present (contract + salary fields).
4. **New keys:** Jooble `au` + `us` domains if free quota is enough for smoke; else skip.
5. **New connector candidate:** Findwork.dev (small, clean, high IT).
6. **Partner/gov track:** DWP Find a Job / Jobs & Careers access request; document outcome in catalog (update id 8 notes).
7. **RSS spike:** CWJobs + ACT Jobs from non-blocked IP; only then open collector tickets.

---

## Primary references

- Adzuna API overview: https://developer.adzuna.com/overview
- Reed Jobseeker API: https://www.reed.co.uk/developers/jobseeker
- USAJOBS quick start / auth: https://developer.usajobs.gov/general/quick-start · https://developer.usajobs.gov/Guides/Authentication
- Jooble REST API: https://help.jooble.org/en/support/solutions/articles/60001448238-rest-api-documentation
- DWP Find a Job catalogue: https://www.api.gov.uk/dwp/find-a-job/ (verify live; may 404 during catalogue publish lag)
- SEEK reflecting job ads (no search): https://developer.seek.com/use-cases/job-posting/reflecting-job-ads
- NLx data access: https://nlxresearchhub.org/data-access
- CWJobs RSS UX: https://www.cwjobs.co.uk/JobSearch/RSSLink.aspx
- ACT Jobs RSS mention: https://www.jobs.act.gov.au/how-we-hire/opportunity-alerts
- LMI for All EOL notice: https://api.lmiforall.org.uk/

## Probe log (this pass)

| Target | Result |
|--------|--------|
| `cwjobs.co.uk/JobSearch/RSS.aspx?Keywords=software` | HTTP **403** |
| `jobs.ac.uk/feeds/type-roles` | HTTP **404** |
| `findajob.dwp.gov.uk/api/search` | **301** → `https://www.jobs.service.gov.uk` |
| `jobs.act.gov.au/rss/subscribe?…=all` | Cloudflare **challenge/403** |
| `api.gov.uk/dwp/find-a-job/` | HTTP **404** at fetch time (catalogue page may be intermittently unavailable; GitHub catalogue PR content still describes the API) |

---

## Catalog follow-ups

When implementing, sync `data/sources/catalog.json` / `generate_source_catalog.py`:

- Update **Find a Job UK DWP** notes (migration + keyed API evidence).
- Update **CWJobs** access_mode → `rss` if feed validates.
- Add **Findwork**, **Adzuna AU/US** as geo notes on existing Adzuna row (or child catalog entries).
- Mark **SEEK** search as `REJECTED` for market-intel pull (keep partner posting note if useful elsewhere).
