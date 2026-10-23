# Source endpoint & page-structure analysis workbook

Working document for precise extraction: for **every** catalog source we record the HTTP endpoint (or feed/board URL), auth, response/page shape, and field mapping into `RawJob`.

| | |
|---|---|
| Generated | 2026-10-21 |
| Catalog | [`data/sources/catalog.json`](../../data/sources/catalog.json) |
| Collectors | `backend/app/collectors/*.py` |
| Regenerate | `python3 backend/scripts/generate_endpoint_page_analysis.py` |
| Live probe | [VALIDATION_REPORT.md](VALIDATION_REPORT.md) |
| Detailed sheets | [`analysis/`](analysis/README.md) — one `{key}.md` per connector |
| Procedure | [SPEC-sources.md](../specs/SPEC-sources.md) · ADR-003 authorized connectors only |

## How to fill a source

Write/update `docs/sources/analysis/{connector_key}.md`, then re-run this generator so the tracker Analysis column reflects `| Analysis | DONE |`.

For each entry, complete in order:

1. **Endpoint** — method, URL template, auth, rate limits, pagination.
2. **Payload / page structure** — top-level JSON keys or RSS/HTML selectors; one sample job item.
3. **Field map** — source field → `RawJob` (`source_job_id`, `url`, `title`, `company`, `description`, `location`, `published_at`, `salary_text`, `tags`, `job_type`, `remote_hint`).
4. **Evidence** — last successful probe date + `records_n`; thin vs standard.
5. Set **Analysis** to `DONE` only when 1–4 are verified (code + live or code-only for scaffolds).

Analysis: `TODO` · `PARTIAL` · `PARTIAL_SCAFFOLD` · `DONE` · `SKIP` · `N/A_HELPER` · `TODO_REF`.

### Template

```markdown
#### Endpoint
- Method / URL:
- Auth:
- Query / body:
- Pagination:
- Rate limit / ToS:

#### Payload / page structure
- Content-Type:
- Path to job list:
- Per-item schema:
- Sample (redacted) item:

#### Field map → RawJob
| Source field | RawJob | Notes |
|--------------|--------|-------|
| | source_job_id | |
| | url | |
| | title | |
| | company | |
| | description | |
| | location | |
| | published_at | |
| | salary_text | |
| | tags | |

#### Gaps / precision risks
- 
```

## Tracker (all sources)

| ID | Key | Name | Status | Cat | Analysis | Primary endpoint (from code/catalog) |
|----|-----|------|--------|-----|----------|--------------------------------------|
| 4 | `remotive` | Remotive | ACTIVE | A | DONE | https://remotive.com/api/remote-jobs |
| 5 | `arbeitnow` | Arbeitnow | ACTIVE | A | DONE | https://www.arbeitnow.com/api/job-board-api |
| 6 | `themuse` | The Muse | ACTIVE | A | DONE | https://www.themuse.com/api/public/jobs |
| 17 | `reed` | Reed | ACTIVE | A | DONE | https://www.reed.co.uk/jobs/rss |
| 24 | `tecnoempleo` | Tecnoempleo | ACTIVE | A | DONE | https://www.tecnoempleo.com/alertas-empleo-rss.php |
| 35 | `le_forem` | Le Forem | ACTIVE | A | DONE | https://www.odwb.be/explore/dataset/offres-d-emploi-forem/ |
| 40 | `arbetsformedlingen` | Arbetsförmedlingen | ACTIVE | A | DONE | https://jobsearch.api.jobtechdev.se/search |
| 41 | `nav_stilling_feed` | NAV Stillingsfeed | ACTIVE | A | DONE | https://arbeidsplassen.nav.no/stillinger/stilling/{uuid} |
| 62 | `weworkremotely` | We Work Remotely | ACTIVE | B | DONE | https://weworkremotely.com/categories/remote-programming-jobs.rss |
| 63 | `remoteok` | Remote OK | ACTIVE | B | DONE | https://remoteok.com/api |
| 64 | `working_nomads` | Working Nomads | ACTIVE | B | DONE | https://www.workingnomads.com/api/exposed_jobs/ |
| 83 | `greenhouse` | Greenhouse Job Board API | ACTIVE | D | DONE | https://boards-api.greenhouse.io/v1/boards |
| 84 | `lever` | Lever Postings API | ACTIVE | D | DONE | https://api.lever.co/v0/postings |
| 85 | `smartrecruiters` | SmartRecruiters API | ACTIVE | D | DONE | https://api.smartrecruiters.com/v1/companies |
| 86 | `ashby` | Ashby Job Postings | ACTIVE | D | DONE | https://api.ashbyhq.com/posting-api/job-board |
| 87 | `workable` | Workable careers widget | ACTIVE | D | DONE | https://apply.workable.com/api/v1/widget/accounts/{slug} |
| 88 | `workday` | Workday Careers CXS | ACTIVE | D | DONE | https://{host}/wday/cxs/{tenant}/{site}/jobs |
| 92 | `personio` | Personio public career boards | ACTIVE | D | DONE | https://{company}.{self.base_host}/search.json |
| 93 | `teamtailor` | Teamtailor career JSON Feed | ACTIVE | D | DONE | https://{host}/jobs.json |
| 94 | `recruitee` | Recruitee Careers Site offers | ACTIVE | D | DONE | https://{slug}.recruitee.com/api/offers/ |
| 96 | `pinpoint` | Pinpoint postings.json | ACTIVE | D | DONE | https://{subdomain}.pinpointhq.com/postings.json |
| 143 | `ecb_fx` | ECB Data API | ACTIVE | G | DONE | https://data.ecb.europa.eu/help/api/data |
| 145 | `frankfurter` | Frankfurter | ACTIVE | G | DONE | https://api.frankfurter.app/ |
| 170 | `manual_import` | Manual CSV/JSON/XLSX Import | ACTIVE | I | DONE | https://localhost/manual |
| 171 | `jobicy` | Jobicy | ACTIVE | B | DONE | https://jobicy.com/api/v2/remote-jobs |
| 172 | `himalayas` | Himalayas | ACTIVE | B | DONE | https://himalayas.app/jobs/api |
| 173 | `hn_whoishiring` | HN Who is hiring | ACTIVE | B | DONE | https://hn.algolia.com/api/v1/search_by_date |
| 175 | `devitjobs` | DevITJobs | ACTIVE | A | DONE | https://devitjobs.uk/api/jobsLight |
| 176 | `nofluffjobs` | NoFluffJobs | ACTIVE | A | DONE | https://nofluffjobs.com/api/posting |
| 177 | `getonbrd` | Get on Board | ACTIVE | A | DONE | https://www.getonbrd.com/api/v0/search/jobs |
| 178 | `mycareersfuture` | MyCareersFuture | ACTIVE | A | DONE | https://api.mycareersfuture.gov.sg/v2/jobs |
| 179 | `jobup` | JobUp | ACTIVE | A | DONE | https://www.jobup.ch/api/v1/public/search |
| 180 | `nav_arbeidsplassen` | NAV Arbeidsplassen | ACTIVE | A | DONE | https://arbeidsplassen.nav.no/stillinger/api/search |
| 181 | `landing_jobs` | Landing.jobs | ACTIVE | A | DONE | https://landing.jobs/api/v1/jobs |
| 182 | `kalibrr` | Kalibrr | ACTIVE | A | DONE | https://www.kalibrr.com/api/job_board/search |
| 183 | `dou_ua` | DOU.ua | ACTIVE | A | DONE | https://jobs.dou.ua/vacancies/feeds/ |
| 184 | `authentic_jobs` | Authentic Jobs | ACTIVE | A | DONE | https://feeds.feedburner.com/AuthenticJobs |
| 185 | `wantedly` | Wantedly | ACTIVE | A | DONE | https://www.wantedly.com/api/v1/projects |
| 186 | `duunitori` | Duunitori | ACTIVE | A | DONE | https://duunitori.fi/api/v1/jobentries |
| 187 | `jobindex` | Jobindex | ACTIVE | A | DONE | https://www.jobindex.dk/jobsoegning.rss |
| 188 | `wanted` | Wanted | ACTIVE | A | DONE | https://www.wanted.co.kr/api/v4/jobs |
| 189 | `instahyre` | Instahyre | ACTIVE | A | DONE | https://www.instahyre.com/api/v1/job_search/ |
| 190 | `hasjob` | Hasjob | ACTIVE | A | DONE | https://hasjob.co/ |
| 191 | `helloworld_rs` | HelloWorld.rs | ACTIVE | A | DONE | https://helloworld.rs/rss |
| 192 | `posao_hr` | Posao.hr | ACTIVE | A | DONE | https://www.posao.hr/rss |
| 193 | `jobweb_kenya` | Jobweb Kenya | ACTIVE | A | DONE | https://www.jobwebkenya.com/feed/ |
| 195 | `mpsv` | MPSV / Úřad práce — Volná místa | ACTIVE | A | DONE | https://data.mpsv.cz/od/soubory/volna-mista/volna-mista.json |
| 197 | `findmethatdamjob` | findmethatdamjob.nl | ACTIVE | A | DONE | https://gigsignal-api.fly.dev |
| 198 | `devglobaljobs` | Dev Global Jobs | ACTIVE | A | DONE | https://devglobaljobs.com/api/v1/jobs |
| 199 | `viewjobs` | ViewJobs | ACTIVE | A | DONE | https://www.viewjobs.com.au/api/mcp |
| 200 | `okemprego` | okemprego | ACTIVE | A | DONE | https://www.okemprego.com/api/v1/jobs |
| 201 | `jobbank_ca` | Canada Job Bank (open data) | ACTIVE | A | DONE | https://www.jobbank.gc.ca/jobsearch/jobsearch |
| 1 | `adzuna` | Adzuna | NEEDS_CREDENTIALS | A | PARTIAL_SCAFFOLD | https://api.adzuna.com/v1/api/jobs |
| 2 | `jooble` | Jooble | NEEDS_CREDENTIALS | A | PARTIAL_SCAFFOLD | https://jooble.org/api |
| 3 | `careerjet` | Careerjet | NEEDS_CREDENTIALS | A | PARTIAL_SCAFFOLD | https://search.api.careerjet.net/v4/query |
| 7 | `usajobs` | USAJOBS | NEEDS_CREDENTIALS | A | PARTIAL_SCAFFOLD | https://data.usajobs.gov/api/search |
| 8 | `findajob_dwp` | Find a Job UK DWP | NEEDS_CREDENTIALS | A | PARTIAL_SCAFFOLD | https://findajob.dwp.gov.uk/api/search |
| 9 | `—` | EURES | NEEDS_CREDENTIALS | A | TODO | https://eures.europa.eu/ |
| 10 | `—` | Indeed | NEEDS_CREDENTIALS | A | TODO | https://www.indeed.com/ |
| 11 | `—` | LinkedIn Jobs | NEEDS_CREDENTIALS | A | TODO | https://www.linkedin.com/jobs/ |
| 12 | `—` | Glassdoor Jobs | NEEDS_CREDENTIALS | A | TODO | https://www.glassdoor.com/Job/ |
| 16 | `—` | ZipRecruiter | NEEDS_CREDENTIALS | A | TODO | https://www.ziprecruiter.com/ |
| 25 | `infojobs` | InfoJobs | NEEDS_CREDENTIALS | A | PARTIAL_SCAFFOLD | https://api.infojobs.net/api/1/offer |
| 28 | `—` | StepStone | NEEDS_CREDENTIALS | A | TODO | https://www.stepstone.com/ |
| 29 | `—` | XING Jobs | NEEDS_CREDENTIALS | A | TODO | https://www.xing.com/jobs |
| 30 | `bundesagentur` | Bundesagentur für Arbeit | NEEDS_CREDENTIALS | A | PARTIAL_SCAFFOLD | https://rest.arbeitsagentur.de/jobboerse/jobsuche-service/pc/v6/jobs |
| 31 | `france_travail` | France Travail | NEEDS_CREDENTIALS | A | PARTIAL_SCAFFOLD | https://francetravail.io/ |
| 44 | `upwork` | Upwork GraphQL | NEEDS_CREDENTIALS | B | PARTIAL_SCAFFOLD | https://api.upwork.com/graphql |
| 45 | `freelancer` | Freelancer.com projects | NEEDS_CREDENTIALS | B | PARTIAL_SCAFFOLD | https://www.freelancer.com/api |
| 46 | `—` | Toptal | NEEDS_CREDENTIALS | B | TODO | https://www.toptal.com/ |
| 47 | `—` | Contra | NEEDS_CREDENTIALS | B | TODO | https://contra.com/ |
| 48 | `—` | PeoplePerHour | NEEDS_CREDENTIALS | B | TODO | https://www.peopleperhour.com/ |
| 49 | `—` | Guru | NEEDS_CREDENTIALS | B | TODO | https://www.guru.com/ |
| 50 | `—` | Worksome | NEEDS_CREDENTIALS | B | TODO | https://www.worksome.com/ |
| 51 | `—` | YunoJuno | NEEDS_CREDENTIALS | B | TODO | https://www.yunojuno.com/ |
| 52 | `—` | freelancermap | NEEDS_CREDENTIALS | B | TODO | https://www.freelancermap.com/ |
| 53 | `—` | GULP | NEEDS_CREDENTIALS | B | TODO | https://www.gulp.de/ |
| 54 | `—` | Fiverr | NEEDS_CREDENTIALS | B | TODO | https://www.fiverr.com/ |
| 55 | `—` | FlexJobs | NEEDS_CREDENTIALS | B | TODO | https://www.flexjobs.com/ |
| 56 | `—` | Braintrust | NEEDS_CREDENTIALS | B | TODO | https://www.usebraintrust.com/ |
| 57 | `—` | Catalant | NEEDS_CREDENTIALS | B | TODO | https://gocatalant.com/ |
| 58 | `—` | A.Team | NEEDS_CREDENTIALS | B | TODO | https://www.a.team/ |
| 59 | `—` | Lemon.io | NEEDS_CREDENTIALS | B | TODO | https://lemon.io/ |
| 60 | `—` | Arc | NEEDS_CREDENTIALS | B | TODO | https://arc.dev/ |
| 61 | `—` | Gun.io | NEEDS_CREDENTIALS | B | TODO | https://www.gun.io/ |
| 65 | `—` | Wellfound | NEEDS_CREDENTIALS | B | TODO | https://wellfound.com/ |
| 89 | `—` | SAP SuccessFactors Recruiting | NEEDS_CREDENTIALS | D | TODO | https://www.sap.com/ |
| 90 | `—` | Oracle Recruiting | NEEDS_CREDENTIALS | D | TODO | https://www.oracle.com/ |
| 91 | `—` | iCIMS | NEEDS_CREDENTIALS | D | TODO | https://www.icims.com/ |
| 144 | `—` | Open Exchange Rates | NEEDS_CREDENTIALS | G | TODO | https://docs.openexchangerates.org/ |
| 146 | `—` | ExchangeRate-API | NEEDS_CREDENTIALS | G | TODO | https://www.exchangerate-api.com/ |
| 150 | `—` | O*NET Web Services | NEEDS_CREDENTIALS | G | TODO | https://services.onetcenter.org/ |
| 165 | `—` | Programmable Search Engine | NEEDS_CREDENTIALS | I | TODO | https://programmablesearchengine.google.com/ |
| 196 | `findwork` | Findwork.dev | NEEDS_CREDENTIALS | A | PARTIAL_SCAFFOLD | https://findwork.dev/api/jobs/ |
| 97 | `—` | Eurostat | VALIDATED | E | TODO_REF | https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/ |
| 147 | `—` | ISO 4217 | VALIDATED | G | TODO_REF | https://www.iso.org/iso-4217-currency-codes.html |
| 148 | `—` | ISO 3166 | VALIDATED | G | TODO_REF | https://www.iso.org/iso-3166-country-codes.html |
| 149 | `—` | ESCO API | VALIDATED | G | TODO_REF | https://ec.europa.eu/esco/api |
| 163 | `—` | Public APIs | VALIDATED | I | TODO_REF | https://github.com/public-apis/public-apis |
| 164 | `—` | API List | VALIDATED | I | TODO_REF | https://apilist.fun/ |
| 168 | `—` | Schema.org JobPosting | VALIDATED | I | TODO_REF | https://schema.org/JobPosting |
| 174 | `—` | JobTech Taxonomy API | VALIDATED | G | TODO_REF | https://taxonomy.api.jobtechdev.se/ |
| 14 | `—` | Talent.com | UNDER_REVIEW | A | TODO | https://www.talent.com/ |
| 15 | `—` | SimplyHired | UNDER_REVIEW | A | TODO | https://www.simplyhired.com/ |
| 18 | `—` | Totaljobs | UNDER_REVIEW | A | TODO | https://www.totaljobs.com/ |
| 19 | `—` | CV-Library | UNDER_REVIEW | A | TODO | https://www.cv-library.co.uk/ |
| 20 | `—` | CWJobs | UNDER_REVIEW | A | TODO | https://www.cwjobs.co.uk/ |
| 21 | `—` | Technojobs | UNDER_REVIEW | A | TODO | https://www.technojobs.co.uk/ |
| 22 | `—` | Welcome to the Jungle | UNDER_REVIEW | A | TODO | https://www.welcometothejungle.com/ |
| 26 | `—` | jobs.ch | UNDER_REVIEW | A | TODO | https://www.jobs.ch/ |
| 27 | `—` | JobScout24 | UNDER_REVIEW | A | TODO | https://www.jobscout24.ch/ |
| 32 | `—` | APEC | UNDER_REVIEW | A | TODO | https://www.apec.fr/ |
| 33 | `—` | VDAB | UNDER_REVIEW | A | TODO | https://www.vdab.be/ |
| 34 | `—` | Actiris | UNDER_REVIEW | A | TODO | https://www.actiris.brussels/ |
| 36 | `—` | Nationale Vacaturebank | UNDER_REVIEW | A | TODO | https://www.nationalevacaturebank.nl/ |
| 37 | `—` | IrishJobs | UNDER_REVIEW | A | TODO | https://www.irishjobs.ie/ |
| 38 | `—` | Pracuj.pl | UNDER_REVIEW | A | TODO | https://www.pracuj.pl/ |
| 39 | `—` | Jobly | UNDER_REVIEW | A | TODO | https://www.jobly.fi/ |
| 43 | `—` | Malt | UNDER_REVIEW | B | TODO | https://www.malt.com/ |
| 66 | `—` | Flexiple | UNDER_REVIEW | B | TODO | https://flexiple.com/ |
| 67 | `—` | Hays | UNDER_REVIEW | C | TODO | https://www.hays.com/ |
| 68 | `—` | Michael Page | UNDER_REVIEW | C | TODO | https://www.michaelpage.com/ |
| 69 | `—` | Robert Half | UNDER_REVIEW | C | TODO | https://www.roberthalf.com/ |
| 70 | `—` | Randstad | UNDER_REVIEW | C | TODO | https://www.randstad.com/ |
| 71 | `—` | Adecco | UNDER_REVIEW | C | TODO | https://www.adecco.com/ |
| 72 | `—` | Manpower | UNDER_REVIEW | C | TODO | https://www.manpower.com/ |
| 73 | `—` | Experis | UNDER_REVIEW | C | TODO | https://www.experis.com/ |
| 74 | `—` | TEKsystems | UNDER_REVIEW | C | TODO | https://www.teksystems.com/ |
| 75 | `—` | Kforce | UNDER_REVIEW | C | TODO | https://www.kforce.com/ |
| 76 | `—` | Robert Walters | UNDER_REVIEW | C | TODO | https://www.robertwalters.com/ |
| 77 | `—` | Harvey Nash | UNDER_REVIEW | C | TODO | https://www.harveynash.com/ |
| 78 | `—` | Computer Futures | UNDER_REVIEW | C | TODO | https://www.computerfutures.com/ |
| 79 | `—` | Nigel Frank | UNDER_REVIEW | C | TODO | https://www.nigelfrank.com/ |
| 80 | `—` | Huxley | UNDER_REVIEW | C | TODO | https://www.huxley.com/ |
| 81 | `—` | La Fosse | UNDER_REVIEW | C | TODO | https://www.lafosse.com/ |
| 82 | `—` | Brio Digital | UNDER_REVIEW | C | TODO | https://www.briodigital.io/ |
| 95 | `bamboohr` | BambooHR public careers | UNDER_REVIEW | D | PARTIAL_SCAFFOLD | https://{slug}.bamboohr.com/careers/list |
| 98 | `—` | Cedefop Skills-OVATE | UNDER_REVIEW | E | TODO | https://www.cedefop.europa.eu/en/tools/skills-online-vacancies |
| 100 | `—` | OECD Data | UNDER_REVIEW | E | TODO | https://data.oecd.org/ |
| 101 | `—` | ILOSTAT | UNDER_REVIEW | E | TODO | https://ilostat.ilo.org/ |
| 102 | `—` | World Bank Data | UNDER_REVIEW | E | TODO | https://data.worldbank.org/ |
| 103 | `—` | IMF Data | UNDER_REVIEW | E | TODO | https://www.imf.org/en/Data |
| 104 | `—` | UN Data | UNDER_REVIEW | E | TODO | https://data.un.org/ |
| 105 | `—` | US Bureau of Labor Statistics | UNDER_REVIEW | E | TODO | https://www.bls.gov/data/ |
| 106 | `—` | US Census Bureau | UNDER_REVIEW | E | TODO | https://www.census.gov/data.html |
| 107 | `—` | US O*NET | UNDER_REVIEW | E | TODO | https://www.onetonline.org/ |
| 109 | `—` | Statistics Canada | UNDER_REVIEW | E | TODO | https://www.statcan.gc.ca/ |
| 110 | `—` | Australian Bureau of Statistics | UNDER_REVIEW | E | TODO | https://www.abs.gov.au/ |
| 111 | `—` | Australian Labour Market Insights | UNDER_REVIEW | E | TODO | https://labourmarketinsights.gov.au/ |
| 112 | `—` | Statistics New Zealand | UNDER_REVIEW | E | TODO | https://www.stats.govt.nz/ |
| 113 | `—` | Swiss Federal Statistical Office | UNDER_REVIEW | E | TODO | https://www.bfs.admin.ch/ |
| 114 | `—` | Salarium Switzerland | UNDER_REVIEW | E | TODO | https://www.salarium.bfs.admin.ch/ |
| 115 | `—` | SECO Switzerland | UNDER_REVIEW | E | TODO | https://www.seco.admin.ch/ |
| 116 | `—` | ISTAT | UNDER_REVIEW | E | TODO | https://www.istat.it/ |
| 117 | `—` | INPS | UNDER_REVIEW | E | TODO | https://www.inps.it/ |
| 118 | `—` | Unioncamere Excelsior | UNDER_REVIEW | E | TODO | https://excelsior.unioncamere.net/ |
| 119 | `—` | Ministero del Lavoro IT | UNDER_REVIEW | E | TODO | https://www.lavoro.gov.it/ |
| 122 | `—` | UK ONS | UNDER_REVIEW | E | TODO | https://www.ons.gov.uk/ |
| 123 | `—` | UK National Careers Service | UNDER_REVIEW | E | TODO | https://nationalcareers.service.gov.uk/ |
| 124 | `—` | Statistics Netherlands | UNDER_REVIEW | E | TODO | https://www.cbs.nl/ |
| 125 | `—` | Statistics Norway | UNDER_REVIEW | E | TODO | https://www.ssb.no/ |
| 126 | `—` | Statistics Sweden | UNDER_REVIEW | E | TODO | https://www.scb.se/ |
| 127 | `—` | Statistics Finland | UNDER_REVIEW | E | TODO | https://stat.fi/ |
| 128 | `—` | Statistics Denmark | UNDER_REVIEW | E | TODO | https://www.dst.dk/ |
| 129 | `—` | Statistics Poland | UNDER_REVIEW | E | TODO | https://stat.gov.pl/ |
| 131 | `—` | Stack Overflow Developer Survey | UNDER_REVIEW | F | TODO | https://survey.stackoverflow.co/ |
| 132 | `—` | JetBrains Developer Ecosystem | UNDER_REVIEW | F | TODO | https://www.jetbrains.com/lp/devecosystem/ |
| 133 | `—` | GitHub Octoverse | UNDER_REVIEW | F | TODO | https://github.blog/news-insights/octoverse/ |
| 134 | `—` | CNCF Reports | UNDER_REVIEW | F | TODO | https://www.cncf.io/reports/ |
| 135 | `—` | DORA | UNDER_REVIEW | F | TODO | https://dora.dev/ |
| 136 | `—` | Levels.fyi | UNDER_REVIEW | F | TODO | https://www.levels.fyi/ |
| 137 | `—` | Glassdoor | UNDER_REVIEW | F | TODO | https://www.glassdoor.com/ |
| 138 | `—` | PayScale | UNDER_REVIEW | F | TODO | https://www.payscale.com/ |
| 139 | `—` | Salary.com | UNDER_REVIEW | F | TODO | https://www.salary.com/ |
| 140 | `—` | Hays Salary Guides | UNDER_REVIEW | F | TODO | https://www.hays.com/salary-guide |
| 141 | `—` | Robert Half Salary Guides | UNDER_REVIEW | F | TODO | https://www.roberthalf.com/salary-guide |
| 142 | `—` | Michael Page Salary Guides | UNDER_REVIEW | F | TODO | https://www.michaelpage.com/salary-guide |
| 151 | `—` | TED | UNDER_REVIEW | H | TODO | https://ted.europa.eu/ |
| 152 | `—` | EU Funding & Tenders Portal | UNDER_REVIEW | H | TODO | https://ec.europa.eu/info/funding-tenders/opportunities/portal/ |
| 153 | `—` | UK Contracts Finder | UNDER_REVIEW | H | TODO | https://www.contractsfinder.service.gov.uk/ |
| 154 | `—` | UK Find a Tender | UNDER_REVIEW | H | TODO | https://www.find-tender.service.gov.uk/ |
| 155 | `—` | US SAM.gov | UNDER_REVIEW | H | TODO | https://sam.gov/ |
| 156 | `—` | US FPDS | UNDER_REVIEW | H | TODO | https://www.fpds.gov/ |
| 157 | `—` | US GSA eBuy | UNDER_REVIEW | H | TODO | https://www.gsa.gov/ |
| 158 | `—` | CanadaBuys | UNDER_REVIEW | H | TODO | https://canadabuys.canada.ca/ |
| 159 | `—` | AusTender | UNDER_REVIEW | H | TODO | https://www.tenders.gov.au/ |
| 160 | `—` | Swiss SIMAP | UNDER_REVIEW | H | TODO | https://www.simap.ch/ |
| 161 | `—` | Open Contracting Data Standard | UNDER_REVIEW | H | TODO | https://standard.open-contracting.org/ |
| 162 | `—` | Open Contracting Partnership | UNDER_REVIEW | H | TODO | https://www.open-contracting.org/ |
| 167 | `—` | Internet Archive | UNDER_REVIEW | I | TODO | https://archive.org/ |
| 23 | `—` | No Fluff Jobs | DISCOVERED | A | SKIP | https://nofluffjobs.com/ |
| 42 | `—` | InfoJobs Spain | DISCOVERED | A | SKIP | https://www.infojobs.net/ |
| 99 | `—` | ESCO | DISCOVERED | E | SKIP | https://esco.ec.europa.eu/ |
| 108 | `—` | USAJOBS (stats ref) | DISCOVERED | E | SKIP | https://developer.usajobs.gov/ |
| 120 | `—` | Bundesagentur für Arbeit (stats) | DISCOVERED | E | SKIP | https://www.arbeitsagentur.de/ |
| 121 | `—` | France Travail (stats) | DISCOVERED | E | SKIP | https://www.francetravail.fr/ |
| 130 | `—` | Stats NZ | DISCOVERED | E | SKIP | https://www.stats.govt.nz/ |
| 169 | `—` | Google Job Posting docs | DISCOVERED | I | SKIP | https://developers.google.com/search/docs/appearance/structured-data/job-posting |
| 13 | `—` | Google for Jobs | REJECTED | A | SKIP | https://developers.google.com/search/docs/appearance/structured-data/job-posting |
| 166 | `—` | Common Crawl | REJECTED | I | SKIP | https://commoncrawl.org/ |

**Analysis progress:** `DONE`=52, `PARTIAL_SCAFFOLD`=12, `SKIP`=10, `TODO`=118, `TODO_REF`=8

---

## Detail sheets — ACTIVE

Endpoint pre-filled from collector `base_url` / constants. Full payload + field maps live in [`analysis/`](analysis/) when Analysis=`DONE`.

### Arbeitnow (`arbeitnow`)

- **Catalog ID:** 5 · **Category:** A · **Access:** public_api
- **Verification:** ACTIVE · **Analysis:** DONE
- **Collector:** `backend/app/collectors/arbeitnow.py` · **class:** `ArbeitnowCollector` · **collection_mode:** `dump`
- **Official:** https://www.arbeitnow.com/ · **Docs:** https://www.arbeitnow.com/api/job-board-api
- **Catalog notes:** Live GET 200; connector implemented and tested.
- **Detailed analysis:** [`analysis/arbeitnow.md`](analysis/arbeitnow.md)

#### Endpoint
- **Primary URL:** `https://www.arbeitnow.com/api/job-board-api`
- See detailed sheet for method/auth/pagination, payload, field map, gaps.

---

### Arbetsförmedlingen (`arbetsformedlingen`)

- **Catalog ID:** 40 · **Category:** A · **Access:** open_data
- **Verification:** ACTIVE · **Analysis:** DONE
- **Collector:** `backend/app/collectors/arbetsformedlingen.py` · **class:** `ArbetsformedlingenCollector` · **collection_mode:** `search`
- **Official:** https://arbetsformedlingen.se/ · **Docs:** https://jobsearch.api.jobtechdev.se/
- **Catalog notes:** JobTech JobSearch GET /search live 200 (2026-10-20); public, no API key. Connector implemented.
- **Detailed analysis:** [`analysis/arbetsformedlingen.md`](analysis/arbetsformedlingen.md)

#### Endpoint
- **Primary URL:** `https://jobsearch.api.jobtechdev.se/search`
- **Other URLs in collector:**
  - `https://arbetsformedlingen.se/platsbanken/annonser/{job_id}`
- See detailed sheet for method/auth/pagination, payload, field map, gaps.

---

### Ashby Job Postings (`ashby`)

- **Catalog ID:** 86 · **Category:** D · **Access:** public_api_per_org
- **Verification:** ACTIVE · **Analysis:** DONE
- **Collector:** `backend/app/collectors/ats_boards.py` · **class:** `AshbyCollector` · **collection_mode:** `dump`
- **Official:** https://developers.ashbyhq.com/ · **Docs:** https://developers.ashbyhq.com/
- **Catalog notes:** Public posting API. Defaults ASHBY_ORGS=51 orgs (multi-agent probe 2026-10-21). Empty → non-runnable.
- **Detailed analysis:** [`analysis/ashby.md`](analysis/ashby.md)

#### Endpoint
- **Primary URL:** `https://api.ashbyhq.com/posting-api/job-board`
- See detailed sheet for method/auth/pagination, payload, field map, gaps.

---

### Authentic Jobs (`authentic_jobs`)

- **Catalog ID:** 184 · **Category:** A · **Access:** public_api
- **Verification:** ACTIVE · **Analysis:** DONE
- **Collector:** `backend/app/collectors/authentic_jobs.py` · **class:** `AuthenticJobsCollector` · **collection_mode:** `feed`
- **Official:** https://authenticjobs.com/ · **Docs:** https://feeds.feedburner.com/AuthenticJobs
- **Catalog notes:** Free design/dev jobs RSS via FeedBurner (site /rss is editorial). No key.
- **Detailed analysis:** [`analysis/authentic_jobs.md`](analysis/authentic_jobs.md)

#### Endpoint
- **Primary URL:** `https://feeds.feedburner.com/AuthenticJobs`
- **Named constants:**
  - `RSS_URL` = `https://feeds.feedburner.com/AuthenticJobs`
- See detailed sheet for method/auth/pagination, payload, field map, gaps.

---

### Dev Global Jobs (`devglobaljobs`)

- **Catalog ID:** 198 · **Category:** A · **Access:** public_api
- **Verification:** ACTIVE · **Analysis:** DONE
- **Collector:** `backend/app/collectors/devglobaljobs.py` · **class:** `DevGlobalJobsCollector` · **collection_mode:** `dump`
- **Official:** https://devglobaljobs.com/ · **Docs:** https://devglobaljobs.com/developers
- **Catalog notes:** Free display API (no key; 120 req/min/IP). Attribution required. Default countries LU,BG via DEVGLOBALJOBS_COUNTRIES — fills LU/BG geo gaps. Live HTTP probe 200 (2026-10-21). Aggregator of public listings; not a national PES.
- **Detailed analysis:** [`analysis/devglobaljobs.md`](analysis/devglobaljobs.md)

#### Endpoint
- **Primary URL:** `https://devglobaljobs.com/api/v1/jobs`
- **Named constants:**
  - `API_URL` = `https://devglobaljobs.com/api/v1/jobs`
- See detailed sheet for method/auth/pagination, payload, field map, gaps.

---

### DevITJobs (`devitjobs`)

- **Catalog ID:** 175 · **Category:** A · **Access:** public_api
- **Verification:** ACTIVE · **Analysis:** DONE
- **Collector:** `backend/app/collectors/devitjobs.py` · **class:** `DevITJobsCollector` · **collection_mode:** `dump`
- **Official:** https://devitjobs.uk/ · **Docs:** https://devitjobs.uk/api/jobsLight
- **Catalog notes:** Free jobsLight JSON (uk/com hosts). No key. Good UK/IT coverage; prefer over paid aggregators.
- **Detailed analysis:** [`analysis/devitjobs.md`](analysis/devitjobs.md)

#### Endpoint
- **Primary URL:** `https://devitjobs.uk/api/jobsLight`
- **Other URLs in collector:**
  - `https://devitjobs.{host}/api/jobsLight`
- See detailed sheet for method/auth/pagination, payload, field map, gaps.

---

### DOU.ua (`dou_ua`)

- **Catalog ID:** 183 · **Category:** A · **Access:** public_api
- **Verification:** ACTIVE · **Analysis:** DONE
- **Collector:** `backend/app/collectors/dou_ua.py` · **class:** `DouUaCollector` · **collection_mode:** `feed`
- **Official:** https://jobs.dou.ua/ · **Docs:** https://jobs.dou.ua/vacancies/feeds/
- **Catalog notes:** Free Ukrainian IT category RSS feeds. No key. Default category Java.
- **Detailed analysis:** [`analysis/dou_ua.md`](analysis/dou_ua.md)

#### Endpoint
- **Primary URL:** `https://jobs.dou.ua/vacancies/feeds/`
- **Named constants:**
  - `RSS_URL` = `https://jobs.dou.ua/vacancies/feeds/`
- See detailed sheet for method/auth/pagination, payload, field map, gaps.

---

### Duunitori (`duunitori`)

- **Catalog ID:** 186 · **Category:** A · **Access:** public_api
- **Verification:** ACTIVE · **Analysis:** DONE
- **Collector:** `backend/app/collectors/duunitori.py` · **class:** `DuunitoriCollector` · **collection_mode:** `search`
- **Official:** https://duunitori.fi/ · **Docs:** https://duunitori.fi/api/v1/jobentries
- **Catalog notes:** Free Finland jobentries JSON search. No key. Detail URL from slug.
- **Detailed analysis:** [`analysis/duunitori.md`](analysis/duunitori.md)

#### Endpoint
- **Primary URL:** `https://duunitori.fi/api/v1/jobentries`
- **Named constants:**
  - `BASE_URL` = `https://duunitori.fi/api/v1/jobentries`
  - `DETAIL_URL` = `https://duunitori.fi/tyopaikat/tyo/{slug}`
- See detailed sheet for method/auth/pagination, payload, field map, gaps.

---

### ECB Data API (`ecb_fx`)

- **Catalog ID:** 143 · **Category:** G · **Access:** public_api
- **Verification:** ACTIVE · **Analysis:** DONE
- **Official:** https://data.ecb.europa.eu/help/api/data · **Docs:** https://data.ecb.europa.eu/help/api/data
- **Catalog notes:** EXR probe 200; FX helper implemented.
- **Detailed analysis:** [`analysis/ecb_fx.md`](analysis/ecb_fx.md)

#### Endpoint
- **Primary URL:** `https://data.ecb.europa.eu/help/api/data`
- See detailed sheet for method/auth/pagination, payload, field map, gaps.

---

### findmethatdamjob.nl (`findmethatdamjob`)

- **Catalog ID:** 197 · **Category:** A · **Access:** public_api
- **Verification:** ACTIVE · **Analysis:** DONE
- **Collector:** `backend/app/collectors/findmethatdamjob.py` · **class:** `FindMeThatDamJobCollector` · **collection_mode:** `search`
- **Official:** https://findmethatdamjob.nl/ · **Docs:** https://findmethatdamjob.nl/docs/api/
- **Catalog notes:** Free documented NL jobs API (gigsignal-api.fly.dev; location=amsterdam = NL-wide). Careers-page aggregator — not UWV/Werk.nl PES. ADR-003: no Werk.nl scrape.
- **Detailed analysis:** [`analysis/findmethatdamjob.md`](analysis/findmethatdamjob.md)

#### Endpoint
- **Primary URL:** `https://gigsignal-api.fly.dev`
- **Named constants:**
  - `API_BASE` = `https://gigsignal-api.fly.dev`
- See detailed sheet for method/auth/pagination, payload, field map, gaps.

---

### Frankfurter (`frankfurter`)

- **Catalog ID:** 145 · **Category:** G · **Access:** public_api
- **Verification:** ACTIVE · **Analysis:** DONE
- **Official:** https://www.frankfurter.app/ · **Docs:** https://api.frankfurter.app/
- **Catalog notes:** Live rates 200; FX helper primary.
- **Detailed analysis:** [`analysis/frankfurter.md`](analysis/frankfurter.md)

#### Endpoint
- **Primary URL:** `https://api.frankfurter.app/`
- See detailed sheet for method/auth/pagination, payload, field map, gaps.

---

### Get on Board (`getonbrd`)

- **Catalog ID:** 177 · **Category:** A · **Access:** public_api
- **Verification:** ACTIVE · **Analysis:** DONE
- **Collector:** `backend/app/collectors/getonbrd.py` · **class:** `GetOnBoardCollector` · **collection_mode:** `dump`
- **Official:** https://www.getonbrd.com/ · **Docs:** https://www.getonbrd.com/api/v0/search/jobs
- **Catalog notes:** Free LATAM tech jobs JSON API (search + programming category). Often posts monthly salaries. No key.
- **Detailed analysis:** [`analysis/getonbrd.md`](analysis/getonbrd.md)

#### Endpoint
- **Primary URL:** `https://www.getonbrd.com/api/v0/search/jobs`
- **Named constants:**
  - `SEARCH_URL` = `https://www.getonbrd.com/api/v0/search/jobs`
  - `CATEGORY_URL` = `https://www.getonbrd.com/api/v0/categories/programming/jobs`
- **Other URLs in collector:**
  - `https://www.getonbrd.com/jobs/{job_id}`
- See detailed sheet for method/auth/pagination, payload, field map, gaps.

---

### Greenhouse Job Board API (`greenhouse`)

- **Catalog ID:** 83 · **Category:** D · **Access:** public_api_per_board
- **Verification:** ACTIVE · **Analysis:** DONE
- **Collector:** `backend/app/collectors/ats_boards.py` · **class:** `GreenhouseCollector` · **collection_mode:** `dump`
- **Official:** https://developers.greenhouse.io/job-board.html · **Docs:** https://developers.greenhouse.io/job-board.html
- **Catalog notes:** Per-board public API. Defaults GREENHOUSE_BOARDS=69 tenants (multi-agent probe 2026-10-21). Empty → non-runnable.
- **Detailed analysis:** [`analysis/greenhouse.md`](analysis/greenhouse.md)

#### Endpoint
- **Primary URL:** `https://boards-api.greenhouse.io/v1/boards`
- See detailed sheet for method/auth/pagination, payload, field map, gaps.

---

### Hasjob (`hasjob`)

- **Catalog ID:** 190 · **Category:** A · **Access:** public_api
- **Verification:** ACTIVE · **Analysis:** DONE
- **Collector:** `backend/app/collectors/hasjob.py` · **class:** `HasjobCollector` · **collection_mode:** `dump`
- **Official:** https://hasjob.co/ · **Docs:** https://hasjob.co/?format=json
- **Catalog notes:** Free India/tech jobs JSON board (?format=json). No key.
- **Detailed analysis:** [`analysis/hasjob.md`](analysis/hasjob.md)

#### Endpoint
- **Primary URL:** `https://hasjob.co/`
- **Named constants:**
  - `BASE_URL` = `https://hasjob.co/`
- **Other URLs in collector:**
  - `https://hasjob.co{path}`
- See detailed sheet for method/auth/pagination, payload, field map, gaps.

---

### HelloWorld.rs (`helloworld_rs`)

- **Catalog ID:** 191 · **Category:** A · **Access:** public_api
- **Verification:** ACTIVE · **Analysis:** DONE
- **Collector:** `backend/app/collectors/helloworld_rs.py` · **class:** `HelloworldRsCollector` · **collection_mode:** `feed`
- **Official:** https://www.helloworld.rs/ · **Docs:** https://helloworld.rs/rss
- **Catalog notes:** Free Serbian IT jobs RSS. No key.
- **Detailed analysis:** [`analysis/helloworld_rs.md`](analysis/helloworld_rs.md)

#### Endpoint
- **Primary URL:** `https://helloworld.rs/rss`
- **Named constants:**
  - `RSS_URL` = `https://helloworld.rs/rss`
- See detailed sheet for method/auth/pagination, payload, field map, gaps.

---

### Himalayas (`himalayas`)

- **Catalog ID:** 172 · **Category:** B · **Access:** public_api
- **Verification:** ACTIVE · **Analysis:** DONE
- **Collector:** `backend/app/collectors/himalayas.py` · **class:** `HimalayasCollector` · **collection_mode:** `dump`
- **Official:** https://himalayas.app/ · **Docs:** https://himalayas.app/jobs/api
- **Catalog notes:** Free public jobs API 200 (2026-10-20). No key. Prefer over paid aggregator APIs.
- **Detailed analysis:** [`analysis/himalayas.md`](analysis/himalayas.md)

#### Endpoint
- **Primary URL:** `https://himalayas.app/jobs/api`
- See detailed sheet for method/auth/pagination, payload, field map, gaps.

---

### HN Who is hiring (`hn_whoishiring`)

- **Catalog ID:** 173 · **Category:** B · **Access:** public_api
- **Verification:** ACTIVE · **Analysis:** DONE
- **Collector:** `backend/app/collectors/hn_whoishiring.py` · **class:** `HnWhoIsHiringCollector` · **collection_mode:** `feed`
- **Official:** https://news.ycombinator.com/ · **Docs:** https://hn.algolia.com/api
- **Catalog notes:** Monthly Who is hiring via Algolia public API (not HTML scrape). Filters seeking-work comments.
- **Detailed analysis:** [`analysis/hn_whoishiring.md`](analysis/hn_whoishiring.md)

#### Endpoint
- **Primary URL:** `https://hn.algolia.com/api/v1/search_by_date`
- **Other URLs in collector:**
  - `https://news.ycombinator.com/item?id={object_id}`
- See detailed sheet for method/auth/pagination, payload, field map, gaps.

---

### Instahyre (`instahyre`)

- **Catalog ID:** 189 · **Category:** A · **Access:** public_api
- **Verification:** ACTIVE · **Analysis:** DONE
- **Collector:** `backend/app/collectors/instahyre.py` · **class:** `InstahyreCollector` · **collection_mode:** `search`
- **Official:** https://www.instahyre.com/ · **Docs:** https://www.instahyre.com/api/v1/job_search/
- **Catalog notes:** Free India tech job search JSON. No key.
- **Detailed analysis:** [`analysis/instahyre.md`](analysis/instahyre.md)

#### Endpoint
- **Primary URL:** `https://www.instahyre.com/api/v1/job_search/`
- **Named constants:**
  - `BASE_URL` = `https://www.instahyre.com/api/v1/job_search/`
- See detailed sheet for method/auth/pagination, payload, field map, gaps.

---

### Canada Job Bank (open data) (`jobbank_ca`)

- **Catalog ID:** 201 · **Category:** A · **Access:** open_data
- **Verification:** ACTIVE · **Analysis:** DONE
- **Collector:** `backend/app/collectors/jobbank_ca.py` · **class:** `JobBankCaCollector` · **collection_mode:** `dump`
- **Official:** https://www.jobbank.gc.ca/ · **Docs:** https://open.canada.ca/data/en/dataset/ea639e28-c0fc-48bf-b5dd-b8899bd43072
- **Catalog notes:** ESDC monthly Job Bank CSV (Open Government Licence – Canada). CKAN package_show picks latest EN all-job-postings TSV; IT via NOC21 212/2222 + title keywords. Snapshot IDs are point-in-time — URL is Job Bank search deep-link (not expired /jobposting/). No HTML scrape (ADR-003).
- **Detailed analysis:** [`analysis/jobbank_ca.md`](analysis/jobbank_ca.md)

#### Endpoint
- **Primary URL:** `https://www.jobbank.gc.ca/jobsearch/jobsearch`
- **Named constants:**
  - `SEARCH_URL` = `https://www.jobbank.gc.ca/jobsearch/jobsearch`
- See detailed sheet for method/auth/pagination, payload, field map, gaps.

---

### Jobicy (`jobicy`)

- **Catalog ID:** 171 · **Category:** B · **Access:** public_api
- **Verification:** ACTIVE · **Analysis:** DONE
- **Collector:** `backend/app/collectors/jobicy.py` · **class:** `JobicyCollector` · **collection_mode:** `dump`
- **Official:** https://jobicy.com/ · **Docs:** https://jobicy.com/api/v2/remote-jobs
- **Catalog notes:** Free public remote API 200 (2026-10-20). Attribution to Jobicy required. Prefer over paid aggregator APIs.
- **Detailed analysis:** [`analysis/jobicy.md`](analysis/jobicy.md)

#### Endpoint
- **Primary URL:** `https://jobicy.com/api/v2/remote-jobs`
- See detailed sheet for method/auth/pagination, payload, field map, gaps.

---

### Jobindex (`jobindex`)

- **Catalog ID:** 187 · **Category:** A · **Access:** public_api
- **Verification:** ACTIVE · **Analysis:** DONE
- **Collector:** `backend/app/collectors/jobindex.py` · **class:** `JobindexCollector` · **collection_mode:** `feed`
- **Official:** https://www.jobindex.dk/ · **Docs:** https://www.jobindex.dk/jobsoegning.rss
- **Catalog notes:** Free Danish jobs RSS (?q=). No key.
- **Detailed analysis:** [`analysis/jobindex.md`](analysis/jobindex.md)

#### Endpoint
- **Primary URL:** `https://www.jobindex.dk/jobsoegning.rss`
- **Named constants:**
  - `RSS_URL` = `https://www.jobindex.dk/jobsoegning.rss`
- See detailed sheet for method/auth/pagination, payload, field map, gaps.

---

### JobUp (`jobup`)

- **Catalog ID:** 179 · **Category:** A · **Access:** public_api
- **Verification:** ACTIVE · **Analysis:** DONE
- **Collector:** `backend/app/collectors/jobup.py` · **class:** `JobUpCollector` · **collection_mode:** `search`
- **Official:** https://www.jobup.ch/ · **Docs:** https://www.jobup.ch/api/v1/public/search
- **Catalog notes:** Free public Swiss jobs search JSON. No key. Prefer query= for IT filters.
- **Detailed analysis:** [`analysis/jobup.md`](analysis/jobup.md)

#### Endpoint
- **Primary URL:** `https://www.jobup.ch/api/v1/public/search`
- **Named constants:**
  - `BASE_URL` = `https://www.jobup.ch/api/v1/public/search`
- See detailed sheet for method/auth/pagination, payload, field map, gaps.

---

### Jobweb Kenya (`jobweb_kenya`)

- **Catalog ID:** 193 · **Category:** A · **Access:** public_api
- **Verification:** ACTIVE · **Analysis:** DONE
- **Collector:** `backend/app/collectors/jobweb_kenya.py` · **class:** `JobwebKenyaCollector` · **collection_mode:** `feed`
- **Official:** https://www.jobwebkenya.com/ · **Docs:** https://www.jobwebkenya.com/feed/
- **Catalog notes:** Free Kenya jobs RSS. No key. First Africa ACTIVE connector.
- **Detailed analysis:** [`analysis/jobweb_kenya.md`](analysis/jobweb_kenya.md)

#### Endpoint
- **Primary URL:** `https://www.jobwebkenya.com/feed/`
- **Named constants:**
  - `RSS_URL` = `https://www.jobwebkenya.com/feed/`
- See detailed sheet for method/auth/pagination, payload, field map, gaps.

---

### Kalibrr (`kalibrr`)

- **Catalog ID:** 182 · **Category:** A · **Access:** public_api
- **Verification:** ACTIVE · **Analysis:** DONE
- **Collector:** `backend/app/collectors/kalibrr.py` · **class:** `KalibrrCollector` · **collection_mode:** `search`
- **Official:** https://www.kalibrr.com/ · **Docs:** https://www.kalibrr.com/api/job_board/search
- **Catalog notes:** Free SEA (PH-heavy) job board search JSON. No key.
- **Detailed analysis:** [`analysis/kalibrr.md`](analysis/kalibrr.md)

#### Endpoint
- **Primary URL:** `https://www.kalibrr.com/api/job_board/search`
- **Named constants:**
  - `BASE_URL` = `https://www.kalibrr.com/api/job_board/search`
- See detailed sheet for method/auth/pagination, payload, field map, gaps.

---

### Landing.jobs (`landing_jobs`)

- **Catalog ID:** 181 · **Category:** A · **Access:** public_api
- **Verification:** ACTIVE · **Analysis:** DONE
- **Collector:** `backend/app/collectors/landing_jobs.py` · **class:** `LandingJobsCollector` · **collection_mode:** `dump`
- **Official:** https://landing.jobs/ · **Docs:** https://landing.jobs/api/v1/jobs
- **Catalog notes:** Free EU tech jobs JSON with EUR gross salary bands. Client-side query filter. No key.
- **Detailed analysis:** [`analysis/landing_jobs.md`](analysis/landing_jobs.md)

#### Endpoint
- **Primary URL:** `https://landing.jobs/api/v1/jobs`
- **Named constants:**
  - `BASE_URL` = `https://landing.jobs/api/v1/jobs`
- See detailed sheet for method/auth/pagination, payload, field map, gaps.

---

### Le Forem (`le_forem`)

- **Catalog ID:** 35 · **Category:** A · **Access:** open_data
- **Verification:** ACTIVE · **Analysis:** DONE
- **Collector:** `backend/app/collectors/le_forem.py` · **class:** `LeForemCollector` · **collection_mode:** `dump`
- **Official:** https://www.leforem.be/ · **Docs:** https://www.odwb.be/explore/dataset/offres-d-emploi-forem/
- **Catalog notes:** Free Wallonia BE ODWB open data (Explore API records, dump cap 200). No key. Partner HR-XML / VDAB out of scope. ADR-003 open data only.
- **Detailed analysis:** [`analysis/le_forem.md`](analysis/le_forem.md)

#### Endpoint
- **Primary URL:** `https://www.odwb.be/explore/dataset/offres-d-emploi-forem/`
- See detailed sheet for method/auth/pagination, payload, field map, gaps.

---

### Lever Postings API (`lever`)

- **Catalog ID:** 84 · **Category:** D · **Access:** public_api_per_site
- **Verification:** ACTIVE · **Analysis:** DONE
- **Collector:** `backend/app/collectors/ats_boards.py` · **class:** `LeverCollector` · **collection_mode:** `dump`
- **Official:** https://github.com/lever/postings-api · **Docs:** https://github.com/lever/postings-api
- **Catalog notes:** Per-site API. Defaults LEVER_SITES=spotify,palantir,wealthfront (probed 2026-10-21). Empty → non-runnable.
- **Detailed analysis:** [`analysis/lever.md`](analysis/lever.md)

#### Endpoint
- **Primary URL:** `https://api.lever.co/v0/postings`
- See detailed sheet for method/auth/pagination, payload, field map, gaps.

---

### Manual CSV/JSON/XLSX Import (`manual_import`)

- **Catalog ID:** 170 · **Category:** I · **Access:** manual_import
- **Verification:** ACTIVE · **Analysis:** DONE
- **Official:** https://localhost/manual · **Docs:** https://localhost/manual
- **Catalog notes:** Lawful structured import path.
- **Detailed analysis:** [`analysis/manual_import.md`](analysis/manual_import.md)

#### Endpoint
- **Primary URL:** `https://localhost/manual`
- See detailed sheet for method/auth/pagination, payload, field map, gaps.

---

### MPSV / Úřad práce — Volná místa (`mpsv`)

- **Catalog ID:** 195 · **Category:** A · **Access:** open_data
- **Verification:** ACTIVE · **Analysis:** DONE
- **Collector:** `backend/app/collectors/mpsv.py` · **class:** `MpsvCollector` · **collection_mode:** `dump`
- **Official:** https://data.mpsv.cz/web/data/volna-mista-za-celou-cr · **Docs:** https://data.mpsv.cz/od/soubory/volna-mista/volna-mista.json
- **Catalog notes:** CZ PES open-data dump (daily). Documented JSON URL 404 as of 2026-10-21; connector falls back to streaming volna-mista.jsonld (~180MB) with bounded IT keyword filter (MAX_RECORDS=300). No auth. Schema: volna-mista.schema.json.
- **Detailed analysis:** [`analysis/mpsv.md`](analysis/mpsv.md)

#### Endpoint
- **Primary URL:** `https://data.mpsv.cz/od/soubory/volna-mista/volna-mista.json`
- **Named constants:**
  - `DUMP_JSON_URL` = `https://data.mpsv.cz/od/soubory/volna-mista/volna-mista.json`
  - `DUMP_JSONLD_URL` = `https://data.mpsv.cz/od/soubory/volna-mista/volna-mista.jsonld`
  - `RESOURCE_BASE` = `https://data.mpsv.cz/zdroj/`
- See detailed sheet for method/auth/pagination, payload, field map, gaps.

---

### MyCareersFuture (`mycareersfuture`)

- **Catalog ID:** 178 · **Category:** A · **Access:** public_api
- **Verification:** ACTIVE · **Analysis:** DONE
- **Collector:** `backend/app/collectors/mycareersfuture.py` · **class:** `MyCareersFutureCollector` · **collection_mode:** `search`
- **Official:** https://www.mycareersfuture.gov.sg/ · **Docs:** https://api.mycareersfuture.gov.sg/v2/jobs
- **Catalog notes:** Free Singapore government jobs API v2 search. No key. Strong APAC IT coverage.
- **Detailed analysis:** [`analysis/mycareersfuture.md`](analysis/mycareersfuture.md)

#### Endpoint
- **Primary URL:** `https://api.mycareersfuture.gov.sg/v2/jobs`
- **Named constants:**
  - `BASE_URL` = `https://api.mycareersfuture.gov.sg/v2/jobs`
- **Other URLs in collector:**
  - `https://www.mycareersfuture.gov.sg/job/{uid}`
- See detailed sheet for method/auth/pagination, payload, field map, gaps.

---

### NAV Arbeidsplassen (`nav_arbeidsplassen`)

- **Catalog ID:** 180 · **Category:** A · **Access:** public_api
- **Verification:** ACTIVE · **Analysis:** DONE
- **Collector:** `backend/app/collectors/nav_arbeidsplassen.py` · **class:** `NavArbeidsplassenCollector` · **collection_mode:** `search`
- **Official:** https://arbeidsplassen.nav.no/ · **Docs:** https://arbeidsplassen.nav.no/stillinger/api/search
- **Catalog notes:** Free Norwegian PES stillinger search JSON (same API as the public UI). No key. Companion dump: nav_stilling_feed (catalog 41) — same vacancy UUIDs; ingest dedupes on canonical_url.
- **Detailed analysis:** [`analysis/nav_arbeidsplassen.md`](analysis/nav_arbeidsplassen.md)

#### Endpoint
- **Primary URL:** `https://arbeidsplassen.nav.no/stillinger/api/search`
- **Named constants:**
  - `BASE_URL` = `https://arbeidsplassen.nav.no/stillinger/api/search`
  - `DETAIL_URL` = `https://arbeidsplassen.nav.no/stillinger/stilling/{uuid}`
- See detailed sheet for method/auth/pagination, payload, field map, gaps.

---

### NAV Stillingsfeed (`nav_stilling_feed`)

- **Catalog ID:** 41 · **Category:** A · **Access:** public_api
- **Verification:** ACTIVE · **Analysis:** DONE
- **Collector:** `backend/app/collectors/nav_stilling_feed.py` · **class:** `NavStillingFeedCollector` · **collection_mode:** `dump`
- **Official:** https://pam-stilling-feed.nav.no/ · **Docs:** https://navikt.github.io/pam-stilling-feed/
- **Catalog notes:** pam-stilling-feed dump (JWT via /api/publicToken; rotates). ACTIVE-only window via If-Modified-Since. Dedupe with nav_arbeidsplassen (search) on same stilling UUID/canonical_url. Private consumer token recommended for production.
- **Detailed analysis:** [`analysis/nav_stilling_feed.md`](analysis/nav_stilling_feed.md)

#### Endpoint
- **Primary URL:** `https://arbeidsplassen.nav.no/stillinger/stilling/{uuid}`
- **Named constants:**
  - `DETAIL_URL` = `https://arbeidsplassen.nav.no/stillinger/stilling/{uuid}`
- See detailed sheet for method/auth/pagination, payload, field map, gaps.

---

### NoFluffJobs (`nofluffjobs`)

- **Catalog ID:** 176 · **Category:** A · **Access:** public_api
- **Verification:** ACTIVE · **Analysis:** DONE
- **Collector:** `backend/app/collectors/nofluffjobs.py` · **class:** `NoFluffJobsCollector` · **collection_mode:** `dump`
- **Official:** https://nofluffjobs.com/ · **Docs:** https://nofluffjobs.com/api/posting
- **Catalog notes:** Free public posting dump (CEE IT; often B2B hourly). Large payload — connector caps + query filter. No key.
- **Detailed analysis:** [`analysis/nofluffjobs.md`](analysis/nofluffjobs.md)

#### Endpoint
- **Primary URL:** `https://nofluffjobs.com/api/posting`
- **Other URLs in collector:**
  - `https://nofluffjobs.com/pl/job/{slug}`
- See detailed sheet for method/auth/pagination, payload, field map, gaps.

---

### okemprego (`okemprego`)

- **Catalog ID:** 200 · **Category:** A · **Access:** public_api
- **Verification:** ACTIVE · **Analysis:** DONE
- **Collector:** `backend/app/collectors/okemprego.py` · **class:** `OkEmpregoCollector` · **collection_mode:** `dump`
- **Official:** https://www.okemprego.com/ · **Docs:** https://www.okemprego.com/pt/api
- **Catalog notes:** Free PT/BR/AO jobs API (no key). Default OKEMPREGO_COUNTRIES=pt + category=it-data. Cite canonical okemprego URL (terms). Complements Landing.jobs for Iberia IT.
- **Detailed analysis:** [`analysis/okemprego.md`](analysis/okemprego.md)

#### Endpoint
- **Primary URL:** `https://www.okemprego.com/api/v1/jobs`
- **Named constants:**
  - `API_URL` = `https://www.okemprego.com/api/v1/jobs`
- See detailed sheet for method/auth/pagination, payload, field map, gaps.

---

### Personio public career boards (`personio`)

- **Catalog ID:** 92 · **Category:** D · **Access:** public_api_per_company
- **Verification:** ACTIVE · **Analysis:** DONE
- **Collector:** `backend/app/collectors/ats_boards.py` · **class:** `PersonioCollector` · **collection_mode:** `dump`
- **Official:** https://www.personio.com/ · **Docs:** https://github.com/personio/api-docs/blob/master/personio-recruiting-api.yaml
- **Catalog notes:** Public listing GET {slug}.jobs.personio.de/search.json (no HTML scrape). Defaults PERSONIO_COMPANIES=15 DACH/EU tech slugs (probed 2026-10-21). Employer Recruiting API remains credentialed separately.
- **Detailed analysis:** [`analysis/personio.md`](analysis/personio.md)

#### Endpoint
- **Primary URL:** `https://{company}.{self.base_host}/search.json`
- See detailed sheet for method/auth/pagination, payload, field map, gaps.

---

### Pinpoint postings.json (`pinpoint`)

- **Catalog ID:** 96 · **Category:** D · **Access:** public_api_per_company
- **Verification:** ACTIVE · **Analysis:** DONE
- **Collector:** `backend/app/collectors/pinpoint.py` · **class:** `PinpointCollector` · **collection_mode:** `dump`
- **Official:** https://www.pinpointhq.com/ · **Docs:** https://developers.pinpointhq.com/docs/jobs-json-endpoint
- **Catalog notes:** Keyless GET https://{subdomain}.pinpointhq.com/postings.json. Defaults PINPOINT_SUBDOMAINS=10 (+hazelcast,smartthings; probed 2026-10-21; skipped DEI demos). Empty → non-runnable.
- **Detailed analysis:** [`analysis/pinpoint.md`](analysis/pinpoint.md)

#### Endpoint
- **Primary URL:** `https://{subdomain}.pinpointhq.com/postings.json`
- **Other URLs in collector:**
  - `https://{subdomain}.pinpointhq.com{item[`
- See detailed sheet for method/auth/pagination, payload, field map, gaps.

---

### Posao.hr (`posao_hr`)

- **Catalog ID:** 192 · **Category:** A · **Access:** public_api
- **Verification:** ACTIVE · **Analysis:** DONE
- **Collector:** `backend/app/collectors/posao_hr.py` · **class:** `PosaoHrCollector` · **collection_mode:** `feed`
- **Official:** https://www.posao.hr/ · **Docs:** https://www.posao.hr/rss
- **Catalog notes:** Free Croatian jobs RSS (general board, filter via query). No key.
- **Detailed analysis:** [`analysis/posao_hr.md`](analysis/posao_hr.md)

#### Endpoint
- **Primary URL:** `https://www.posao.hr/rss`
- **Named constants:**
  - `RSS_URL` = `https://www.posao.hr/rss`
- See detailed sheet for method/auth/pagination, payload, field map, gaps.

---

### Recruitee Careers Site offers (`recruitee`)

- **Catalog ID:** 94 · **Category:** D · **Access:** public_api_per_company
- **Verification:** ACTIVE · **Analysis:** DONE
- **Collector:** `backend/app/collectors/recruitee.py` · **class:** `RecruiteeCollector` · **collection_mode:** `dump`
- **Official:** https://recruitee.com/ · **Docs:** https://docs.recruitee.com/reference/intro-to-careers-site-api
- **Catalog notes:** Keyless GET https://{slug}.recruitee.com/api/offers/ until 2027-02-10. Defaults RECRUITEE_SLUGS=9 slugs (probed 2026-10-21). Empty → non-runnable. Plan X-Careers-Sites-Token after deadline.
- **Detailed analysis:** [`analysis/recruitee.md`](analysis/recruitee.md)

#### Endpoint
- **Primary URL:** `https://{slug}.recruitee.com/api/offers/`
- **Other URLs in collector:**
  - `https://{slug}.recruitee.com/o/{item[`
- See detailed sheet for method/auth/pagination, payload, field map, gaps.

---

### Reed (`reed`)

- **Catalog ID:** 17 · **Category:** A · **Access:** rss
- **Verification:** ACTIVE · **Analysis:** DONE
- **Collector:** `backend/app/collectors/reed.py` · **class:** `ReedCollector` · **collection_mode:** `feed`
- **Official:** https://www.reed.co.uk/ · **Docs:** https://www.reed.co.uk/jobs/rss
- **Catalog notes:** Free public RSS `GET /jobs/rss?keywords=` verified 200. Optional REED_API_KEY for richer JSON API.
- **Detailed analysis:** [`analysis/reed.md`](analysis/reed.md)

#### Endpoint
- **Primary URL:** `https://www.reed.co.uk/jobs/rss`
- **Named constants:**
  - `RSS_URL` = `https://www.reed.co.uk/jobs/rss`
  - `API_URL` = `https://www.reed.co.uk/api/1.0/search`
- See detailed sheet for method/auth/pagination, payload, field map, gaps.

---

### Remote OK (`remoteok`)

- **Catalog ID:** 63 · **Category:** B · **Access:** public_api
- **Verification:** ACTIVE · **Analysis:** DONE
- **Collector:** `backend/app/collectors/remoteok.py` · **class:** `RemoteOKCollector` · **collection_mode:** `dump`
- **Official:** https://remoteok.com/ · **Docs:** https://remoteok.com/api
- **Catalog notes:** API 200; ToS requires attribution link. Connector implemented.
- **Detailed analysis:** [`analysis/remoteok.md`](analysis/remoteok.md)

#### Endpoint
- **Primary URL:** `https://remoteok.com/api`
- See detailed sheet for method/auth/pagination, payload, field map, gaps.

---

### Remotive (`remotive`)

- **Catalog ID:** 4 · **Category:** A · **Access:** public_api
- **Verification:** ACTIVE · **Analysis:** DONE
- **Collector:** `backend/app/collectors/remotive.py` · **class:** `RemotiveCollector` · **collection_mode:** `dump`
- **Official:** https://remotive.com/remote-jobs/api · **Docs:** https://remotive.com/api/remote-jobs
- **Catalog notes:** Live GET 200; connector implemented and tested.
- **Detailed analysis:** [`analysis/remotive.md`](analysis/remotive.md)

#### Endpoint
- **Primary URL:** `https://remotive.com/api/remote-jobs`
- See detailed sheet for method/auth/pagination, payload, field map, gaps.

---

### SmartRecruiters API (`smartrecruiters`)

- **Catalog ID:** 85 · **Category:** D · **Access:** public_api_per_company
- **Verification:** ACTIVE · **Analysis:** DONE
- **Collector:** `backend/app/collectors/smartrecruiters.py` · **class:** `SmartRecruitersCollector` · **collection_mode:** `dump`
- **Official:** https://developers.smartrecruiters.com/ · **Docs:** https://developers.smartrecruiters.com/
- **Catalog notes:** Public postings API. Defaults SMARTRECRUITERS_COMPANIES include endava,ServiceNow,DeliveryHero,Wise,Allegro,Uber (probed 2026-10-20). Empty → non-runnable.
- **Detailed analysis:** [`analysis/smartrecruiters.md`](analysis/smartrecruiters.md)

#### Endpoint
- **Primary URL:** `https://api.smartrecruiters.com/v1/companies`
- **Other URLs in collector:**
  - `https://jobs.smartrecruiters.com/{ident}/{job_id}-{_slug(title)}`
- See detailed sheet for method/auth/pagination, payload, field map, gaps.

---

### Teamtailor career JSON Feed (`teamtailor`)

- **Catalog ID:** 93 · **Category:** D · **Access:** public_api_per_host
- **Verification:** ACTIVE · **Analysis:** DONE
- **Collector:** `backend/app/collectors/teamtailor.py` · **class:** `TeamtailorCollector` · **collection_mode:** `dump`
- **Official:** https://www.teamtailor.com/ · **Docs:** https://support.teamtailor.com/en/articles/5963369-use-our-teamtailor-api
- **Catalog notes:** Keyless GET https://{host}/jobs.json (JSON Feed items). Defaults TEAMTAILOR_HOSTS=26 Nordic/EU hosts (probed 2026-10-21). Empty → non-runnable. JSON:API remains tenant-keyed.
- **Detailed analysis:** [`analysis/teamtailor.md`](analysis/teamtailor.md)

#### Endpoint
- **Primary URL:** `https://{host}/jobs.json`
- See detailed sheet for method/auth/pagination, payload, field map, gaps.

---

### Tecnoempleo (`tecnoempleo`)

- **Catalog ID:** 24 · **Category:** A · **Access:** rss
- **Verification:** ACTIVE · **Analysis:** DONE
- **Collector:** `backend/app/collectors/tecnoempleo.py` · **class:** `TecnoempleoCollector` · **collection_mode:** `feed`
- **Official:** https://www.tecnoempleo.com/ · **Docs:** https://www.tecnoempleo.com/alertas-empleo-rss.php
- **Catalog notes:** Free Spain IT RSS (alertas-empleo-rss.php; optional ?te=). ADR-003: RSS only — no Empléate Solr scrape.
- **Detailed analysis:** [`analysis/tecnoempleo.md`](analysis/tecnoempleo.md)

#### Endpoint
- **Primary URL:** `https://www.tecnoempleo.com/alertas-empleo-rss.php`
- **Named constants:**
  - `RSS_URL` = `https://www.tecnoempleo.com/alertas-empleo-rss.php`
- See detailed sheet for method/auth/pagination, payload, field map, gaps.

---

### The Muse (`themuse`)

- **Catalog ID:** 6 · **Category:** A · **Access:** public_api
- **Verification:** ACTIVE · **Analysis:** DONE
- **Collector:** `backend/app/collectors/themuse.py` · **class:** `TheMuseCollector` · **collection_mode:** `dump`
- **Official:** https://www.themuse.com/developers/api/v2 · **Docs:** https://www.themuse.com/api/public/jobs
- **Catalog notes:** Live GET 200 with jobs; connector implemented.
- **Detailed analysis:** [`analysis/themuse.md`](analysis/themuse.md)

#### Endpoint
- **Primary URL:** `https://www.themuse.com/api/public/jobs`
- See detailed sheet for method/auth/pagination, payload, field map, gaps.

---

### ViewJobs (`viewjobs`)

- **Catalog ID:** 199 · **Category:** A · **Access:** public_api
- **Verification:** ACTIVE · **Analysis:** DONE
- **Collector:** `backend/app/collectors/viewjobs.py` · **class:** `ViewJobsCollector` · **collection_mode:** `search`
- **Official:** https://www.viewjobs.com.au/ · **Docs:** https://www.viewjobs.com.au/for-agents
- **Catalog notes:** Free AU jobs MCP (Streamable HTTP /api/mcp search_jobs; no key). Regional + metro Australia. Keep listing URLs (utm attribution). Not Seek scrape — documented agent search surface (ADR-003).
- **Detailed analysis:** [`analysis/viewjobs.md`](analysis/viewjobs.md)

#### Endpoint
- **Primary URL:** `https://www.viewjobs.com.au/api/mcp`
- **Named constants:**
  - `MCP_URL` = `https://www.viewjobs.com.au/api/mcp`
- See detailed sheet for method/auth/pagination, payload, field map, gaps.

---

### Wanted (`wanted`)

- **Catalog ID:** 188 · **Category:** A · **Access:** public_api
- **Verification:** ACTIVE · **Analysis:** DONE
- **Collector:** `backend/app/collectors/wanted.py` · **class:** `WantedCollector` · **collection_mode:** `search`
- **Official:** https://www.wanted.co.kr/ · **Docs:** https://www.wanted.co.kr/api/v4/jobs
- **Catalog notes:** Free Korea jobs JSON (v4). No key. annual_from/to are experience years, not salary.
- **Detailed analysis:** [`analysis/wanted.md`](analysis/wanted.md)

#### Endpoint
- **Primary URL:** `https://www.wanted.co.kr/api/v4/jobs`
- **Named constants:**
  - `BASE_URL` = `https://www.wanted.co.kr/api/v4/jobs`
  - `DETAIL_URL` = `https://www.wanted.co.kr/wd/{id}`
- See detailed sheet for method/auth/pagination, payload, field map, gaps.

---

### Wantedly (`wantedly`)

- **Catalog ID:** 185 · **Category:** A · **Access:** public_api
- **Verification:** ACTIVE · **Analysis:** DONE
- **Collector:** `backend/app/collectors/wantedly.py` · **class:** `WantedlyCollector` · **collection_mode:** `search`
- **Official:** https://www.wantedly.com/ · **Docs:** https://www.wantedly.com/api/v1/projects
- **Catalog notes:** Free Japan projects/jobs JSON search. No key. Strong JP IT coverage.
- **Detailed analysis:** [`analysis/wantedly.md`](analysis/wantedly.md)

#### Endpoint
- **Primary URL:** `https://www.wantedly.com/api/v1/projects`
- **Named constants:**
  - `BASE_URL` = `https://www.wantedly.com/api/v1/projects`
  - `DETAIL_URL` = `https://www.wantedly.com/projects/{id}`
- See detailed sheet for method/auth/pagination, payload, field map, gaps.

---

### We Work Remotely (`weworkremotely`)

- **Catalog ID:** 62 · **Category:** B · **Access:** rss
- **Verification:** ACTIVE · **Analysis:** DONE
- **Collector:** `backend/app/collectors/weworkremotely.py` · **class:** `WeWorkRemotelyCollector` · **collection_mode:** `feed`
- **Official:** https://weworkremotely.com/ · **Docs:** https://weworkremotely.com/categories/remote-programming-jobs.rss
- **Catalog notes:** RSS 200; connector implemented.
- **Detailed analysis:** [`analysis/weworkremotely.md`](analysis/weworkremotely.md)

#### Endpoint
- **Primary URL:** `https://weworkremotely.com/categories/remote-programming-jobs.rss`
- See detailed sheet for method/auth/pagination, payload, field map, gaps.

---

### Workable careers widget (`workable`)

- **Catalog ID:** 87 · **Category:** D · **Access:** public_api_per_company
- **Verification:** ACTIVE · **Analysis:** DONE
- **Collector:** `backend/app/collectors/workable.py` · **class:** `WorkableCollector` · **collection_mode:** `dump`
- **Official:** https://www.workable.com/ · **Docs:** https://help.workable.com/hc/en-us/articles/115012771647
- **Catalog notes:** Keyless GET apply.workable.com/api/v1/widget/accounts/{slug}?details=true. Defaults WORKABLE_SLUGS=huggingface,jasper,skillshare,riot (non-empty boards probed 2026-10-21). Many brand slugs return jobs:[]. Back off on HTTP 429. SPI v3 remains tenant-keyed.
- **Detailed analysis:** [`analysis/workable.md`](analysis/workable.md)

#### Endpoint
- **Primary URL:** `https://apply.workable.com/api/v1/widget/accounts/{slug}`
- See detailed sheet for method/auth/pagination, payload, field map, gaps.

---

### Workday Careers CXS (`workday`)

- **Catalog ID:** 88 · **Category:** D · **Access:** public_api_per_tenant
- **Verification:** ACTIVE · **Analysis:** DONE
- **Collector:** `backend/app/collectors/workday.py` · **class:** `WorkdayCollector` · **collection_mode:** `dump`
- **Official:** https://www.workday.com/ · **Docs:** https://www.workday.com/
- **Catalog notes:** Keyless POST https://{tenant}.{wd}.myworkdayjobs.com/wday/cxs/{tenant}/{site}/jobs. Defaults WORKDAY_TENANTS=37 tech-leaning CXS (multi-agent probe 2026-10-21; retail megaboards omitted). Empty → non-runnable. No cross-tenant search.
- **Detailed analysis:** [`analysis/workday.md`](analysis/workday.md)

#### Endpoint
- **Primary URL:** `https://{host}/wday/cxs/{tenant}/{site}/jobs`
- See detailed sheet for method/auth/pagination, payload, field map, gaps.

---

### Working Nomads (`working_nomads`)

- **Catalog ID:** 64 · **Category:** B · **Access:** public_api
- **Verification:** ACTIVE · **Analysis:** DONE
- **Collector:** `backend/app/collectors/working_nomads.py` · **class:** `WorkingNomadsCollector` · **collection_mode:** `dump`
- **Official:** https://www.workingnomads.com/ · **Docs:** https://www.workingnomads.com/api/exposed_jobs/
- **Catalog notes:** Exposed jobs API 200; connector implemented.
- **Detailed analysis:** [`analysis/working_nomads.md`](analysis/working_nomads.md)

#### Endpoint
- **Primary URL:** `https://www.workingnomads.com/api/exposed_jobs/`
- See detailed sheet for method/auth/pagination, payload, field map, gaps.

---

## Detail sheets — NEEDS_CREDENTIALS (scaffolds)

### Adzuna (`adzuna`)

- **Catalog ID:** 1 · **Analysis:** PARTIAL_SCAFFOLD · **Mode:** `search`
- **Collector:** `backend/app/collectors/adzuna.py` · **class:** `AdzunaCollector`
- **Primary URL:** `https://api.adzuna.com/v1/api/jobs`
- **Credentials:** required (fail-closed). See [CREDENTIALED_CONNECTORS.md](CREDENTIALED_CONNECTORS.md).
- **Detailed analysis:** [`analysis/adzuna.md`](analysis/adzuna.md)

---

### Bundesagentur für Arbeit (`bundesagentur`)

- **Catalog ID:** 30 · **Analysis:** PARTIAL_SCAFFOLD · **Mode:** `search`
- **Collector:** `backend/app/collectors/bundesagentur.py` · **class:** `BundesagenturCollector`
- **Primary URL:** `https://rest.arbeitsagentur.de/jobboerse/jobsuche-service/pc/v6/jobs`
- **Credentials:** required (fail-closed). See [CREDENTIALED_CONNECTORS.md](CREDENTIALED_CONNECTORS.md).
- **Detailed analysis:** [`analysis/bundesagentur.md`](analysis/bundesagentur.md)

---

### Careerjet (`careerjet`)

- **Catalog ID:** 3 · **Analysis:** PARTIAL_SCAFFOLD · **Mode:** `search`
- **Collector:** `backend/app/collectors/careerjet.py` · **class:** `CareerjetCollector`
- **Primary URL:** `https://search.api.careerjet.net/v4/query`
  - `API_URL` = `https://search.api.careerjet.net/v4/query`
- **Credentials:** required (fail-closed). See [CREDENTIALED_CONNECTORS.md](CREDENTIALED_CONNECTORS.md).
- **Detailed analysis:** [`analysis/careerjet.md`](analysis/careerjet.md)

---

### Find a Job UK DWP (`findajob_dwp`)

- **Catalog ID:** 8 · **Analysis:** PARTIAL_SCAFFOLD · **Mode:** `search`
- **Collector:** `backend/app/collectors/findajob_dwp.py` · **class:** `FindAJobDwpCollector`
- **Primary URL:** `https://findajob.dwp.gov.uk/api/search`
- **Credentials:** required (fail-closed). See [CREDENTIALED_CONNECTORS.md](CREDENTIALED_CONNECTORS.md).
- **Detailed analysis:** [`analysis/findajob_dwp.md`](analysis/findajob_dwp.md)

---

### Findwork.dev (`findwork`)

- **Catalog ID:** 196 · **Analysis:** PARTIAL_SCAFFOLD · **Mode:** `search`
- **Collector:** `backend/app/collectors/findwork.py` · **class:** `FindworkCollector`
- **Primary URL:** `https://findwork.dev/api/jobs/`
- **Credentials:** required (fail-closed). See [CREDENTIALED_CONNECTORS.md](CREDENTIALED_CONNECTORS.md).
- **Detailed analysis:** [`analysis/findwork.md`](analysis/findwork.md)

---

### France Travail (`france_travail`)

- **Catalog ID:** 31 · **Analysis:** PARTIAL_SCAFFOLD · **Mode:** `search`
- **Collector:** `backend/app/collectors/france_travail.py` · **class:** `FranceTravailCollector`
- **Primary URL:** `https://francetravail.io/`
- **Credentials:** required (fail-closed). See [CREDENTIALED_CONNECTORS.md](CREDENTIALED_CONNECTORS.md).
- **Detailed analysis:** [`analysis/france_travail.md`](analysis/france_travail.md)

---

### Freelancer.com projects (`freelancer`)

- **Catalog ID:** 45 · **Analysis:** PARTIAL_SCAFFOLD · **Mode:** `search`
- **Collector:** `backend/app/collectors/freelancer.py` · **class:** `FreelancerCollector`
- **Primary URL:** `https://www.freelancer.com/api`
- **Credentials:** required (fail-closed). See [CREDENTIALED_CONNECTORS.md](CREDENTIALED_CONNECTORS.md).
- **Detailed analysis:** [`analysis/freelancer.md`](analysis/freelancer.md)

---

### InfoJobs (`infojobs`)

- **Catalog ID:** 25 · **Analysis:** PARTIAL_SCAFFOLD · **Mode:** `search`
- **Collector:** `backend/app/collectors/infojobs.py` · **class:** `InfoJobsCollector`
- **Primary URL:** `https://api.infojobs.net/api/1/offer`
  - `SEARCH_URL` = `https://api.infojobs.net/api/1/offer`
- **Credentials:** required (fail-closed). See [CREDENTIALED_CONNECTORS.md](CREDENTIALED_CONNECTORS.md).
- **Detailed analysis:** [`analysis/infojobs.md`](analysis/infojobs.md)

---

### Jooble (`jooble`)

- **Catalog ID:** 2 · **Analysis:** PARTIAL_SCAFFOLD · **Mode:** `search`
- **Collector:** `backend/app/collectors/jooble.py` · **class:** `JoobleCollector`
- **Primary URL:** `https://jooble.org/api`
- **Credentials:** required (fail-closed). See [CREDENTIALED_CONNECTORS.md](CREDENTIALED_CONNECTORS.md).
- **Detailed analysis:** [`analysis/jooble.md`](analysis/jooble.md)

---

### Upwork GraphQL (`upwork`)

- **Catalog ID:** 44 · **Analysis:** PARTIAL_SCAFFOLD · **Mode:** `search`
- **Collector:** `backend/app/collectors/upwork.py` · **class:** `UpworkCollector`
- **Primary URL:** `https://api.upwork.com/graphql`
  - `GRAPHQL_URL` = `https://api.upwork.com/graphql`
- **Credentials:** required (fail-closed). See [CREDENTIALED_CONNECTORS.md](CREDENTIALED_CONNECTORS.md).
- **Payload / field map:** _(fill `analysis/{key}.md` from code; live after keys)_

---

### USAJOBS (`usajobs`)

- **Catalog ID:** 7 · **Analysis:** PARTIAL_SCAFFOLD · **Mode:** `search`
- **Collector:** `backend/app/collectors/usajobs.py` · **class:** `USAJobsCollector`
- **Primary URL:** `https://data.usajobs.gov/api/search`
- **Credentials:** required (fail-closed). See [CREDENTIALED_CONNECTORS.md](CREDENTIALED_CONNECTORS.md).
- **Detailed analysis:** [`analysis/usajobs.md`](analysis/usajobs.md)

---

## Detail sheets — VALIDATED (reference / non-job)

### Eurostat (catalog_id=97)
- **URL:** https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/
- **Role:** reference/taxonomy/stats — not job ingest. **Analysis:** TODO_REF if product needs the response schema.
- **Notes:** Free dissemination API via GET /api/v1/stats/eurostat/series. Official statistics reference only — never mixed into observed job KPIs.

### ISO 4217 (catalog_id=147)
- **URL:** https://www.iso.org/iso-4217-currency-codes.html
- **Role:** reference/taxonomy/stats — not job ingest. **Analysis:** TODO_REF if product needs the response schema.
- **Notes:** Currency code standard reference (static).

### ISO 3166 (catalog_id=148)
- **URL:** https://www.iso.org/iso-3166-country-codes.html
- **Role:** reference/taxonomy/stats — not job ingest. **Analysis:** TODO_REF if product needs the response schema.
- **Notes:** Country code standard reference (static).

### ESCO API (catalog_id=149)
- **URL:** https://ec.europa.eu/esco/api
- **Role:** reference/taxonomy/stats — not job ingest. **Analysis:** TODO_REF if product needs the response schema.
- **Notes:** Free public search API validated via GET /api/v1/taxonomy/esco/search. Taxonomy reference only — not a job connector or rate source.

### Public APIs (catalog_id=163)
- **URL:** https://github.com/public-apis/public-apis
- **Role:** reference/taxonomy/stats — not job ingest. **Analysis:** TODO_REF if product needs the response schema.
- **Notes:** Discovery directory only — not a job source.

### API List (catalog_id=164)
- **URL:** https://apilist.fun/
- **Role:** reference/taxonomy/stats — not job ingest. **Analysis:** TODO_REF if product needs the response schema.
- **Notes:** Discovery directory only.

### Schema.org JobPosting (catalog_id=168)
- **URL:** https://schema.org/JobPosting
- **Role:** reference/taxonomy/stats — not job ingest. **Analysis:** TODO_REF if product needs the response schema.
- **Notes:** Schema for normalization.

### JobTech Taxonomy API (catalog_id=174)
- **URL:** https://taxonomy.api.jobtechdev.se/
- **Role:** reference/taxonomy/stats — not job ingest. **Analysis:** TODO_REF if product needs the response schema.
- **Notes:** Free Swedish labour taxonomy autocomplete via GET /api/v1/taxonomy/jobtech/search. Reference only — not jobs/rates.

## Detail sheets — NEEDS_CREDENTIALS without connector

No in-repo collector. Fill only when an authorized API/partner path exists (ADR-003).

### EURES (id=9, cat=A)
- **Official:** https://eures.europa.eu/ · **Docs:** https://eures.europa.eu/
- **Access mode:** partner_api · **Analysis:** TODO
- **Notes:** EURES API typically requires registration; not probed with credentials.
- **Endpoint / payload / field map:** _(not started)_

### Indeed (id=10, cat=A)
- **Official:** https://www.indeed.com/ · **Docs:** https://www.indeed.com/
- **Access mode:** publisher_api · **Analysis:** TODO
- **Notes:** Authorized publisher/partner APIs only. No scraping.
- **Endpoint / payload / field map:** _(not started)_

### LinkedIn Jobs (id=11, cat=A)
- **Official:** https://www.linkedin.com/jobs/ · **Docs:** https://www.linkedin.com/jobs/
- **Access mode:** partner_api · **Analysis:** TODO
- **Notes:** Official partner APIs only. No scraping.
- **Endpoint / payload / field map:** _(not started)_

### Glassdoor Jobs (id=12, cat=A)
- **Official:** https://www.glassdoor.com/Job/ · **Docs:** https://www.glassdoor.com/Job/
- **Access mode:** partner_api · **Analysis:** TODO
- **Notes:** No verified public open API; ToS restricts scraping.
- **Endpoint / payload / field map:** _(not started)_

### ZipRecruiter (id=16, cat=A)
- **Official:** https://www.ziprecruiter.com/ · **Docs:** https://www.ziprecruiter.com/
- **Access mode:** partner_api · **Analysis:** TODO
- **Notes:** Partner integrations; credentials required.
- **Endpoint / payload / field map:** _(not started)_

### StepStone (id=28, cat=A)
- **Official:** https://www.stepstone.com/ · **Docs:** https://www.stepstone.com/
- **Access mode:** partner_api · **Analysis:** TODO
- **Notes:** Commercial partner feeds; credentials required.
- **Endpoint / payload / field map:** _(not started)_

### XING Jobs (id=29, cat=A)
- **Official:** https://www.xing.com/jobs · **Docs:** https://www.xing.com/jobs
- **Access mode:** partner_api · **Analysis:** TODO
- **Notes:** XING APIs require developer/partner access.
- **Endpoint / payload / field map:** _(not started)_

### Toptal (id=46, cat=B)
- **Official:** https://www.toptal.com/ · **Docs:** https://www.toptal.com/
- **Access mode:** partner_or_unknown · **Analysis:** TODO
- **Notes:** No public job dump API.
- **Endpoint / payload / field map:** _(not started)_

### Contra (id=47, cat=B)
- **Official:** https://contra.com/ · **Docs:** https://contra.com/
- **Access mode:** partner_or_unknown · **Analysis:** TODO
- **Notes:** No verified public API.
- **Endpoint / payload / field map:** _(not started)_

### PeoplePerHour (id=48, cat=B)
- **Official:** https://www.peopleperhour.com/ · **Docs:** https://www.peopleperhour.com/
- **Access mode:** partner_or_unknown · **Analysis:** TODO
- **Notes:** No verified public API.
- **Endpoint / payload / field map:** _(not started)_

### Guru (id=49, cat=B)
- **Official:** https://www.guru.com/ · **Docs:** https://www.guru.com/
- **Access mode:** partner_or_unknown · **Analysis:** TODO
- **Notes:** No verified public API.
- **Endpoint / payload / field map:** _(not started)_

### Worksome (id=50, cat=B)
- **Official:** https://www.worksome.com/ · **Docs:** https://www.worksome.com/
- **Access mode:** partner_or_unknown · **Analysis:** TODO
- **Notes:** Enterprise access.
- **Endpoint / payload / field map:** _(not started)_

### YunoJuno (id=51, cat=B)
- **Official:** https://www.yunojuno.com/ · **Docs:** https://www.yunojuno.com/
- **Access mode:** partner_or_unknown · **Analysis:** TODO
- **Notes:** No verified public API.
- **Endpoint / payload / field map:** _(not started)_

### freelancermap (id=52, cat=B)
- **Official:** https://www.freelancermap.com/ · **Docs:** https://www.freelancermap.com/
- **Access mode:** partner_or_unknown · **Analysis:** TODO
- **Notes:** No verified public API; no scraping.
- **Endpoint / payload / field map:** _(not started)_

### GULP (id=53, cat=B)
- **Official:** https://www.gulp.de/ · **Docs:** https://www.gulp.de/
- **Access mode:** partner_or_unknown · **Analysis:** TODO
- **Notes:** No verified public API.
- **Endpoint / payload / field map:** _(not started)_

### Fiverr (id=54, cat=B)
- **Official:** https://www.fiverr.com/ · **Docs:** https://www.fiverr.com/
- **Access mode:** partner_or_unknown · **Analysis:** TODO
- **Notes:** Partner API; credentials.
- **Endpoint / payload / field map:** _(not started)_

### FlexJobs (id=55, cat=B)
- **Official:** https://www.flexjobs.com/ · **Docs:** https://www.flexjobs.com/
- **Access mode:** partner_or_unknown · **Analysis:** TODO
- **Notes:** Paid membership; no open API.
- **Endpoint / payload / field map:** _(not started)_

### Braintrust (id=56, cat=B)
- **Official:** https://www.usebraintrust.com/ · **Docs:** https://www.usebraintrust.com/
- **Access mode:** partner_or_unknown · **Analysis:** TODO
- **Notes:** No verified public API.
- **Endpoint / payload / field map:** _(not started)_

### Catalant (id=57, cat=B)
- **Official:** https://gocatalant.com/ · **Docs:** https://gocatalant.com/
- **Access mode:** partner_or_unknown · **Analysis:** TODO
- **Notes:** Enterprise.
- **Endpoint / payload / field map:** _(not started)_

### A.Team (id=58, cat=B)
- **Official:** https://www.a.team/ · **Docs:** https://www.a.team/
- **Access mode:** partner_or_unknown · **Analysis:** TODO
- **Notes:** Invite network; no public API.
- **Endpoint / payload / field map:** _(not started)_

### Lemon.io (id=59, cat=B)
- **Official:** https://lemon.io/ · **Docs:** https://lemon.io/
- **Access mode:** partner_or_unknown · **Analysis:** TODO
- **Notes:** No verified public API.
- **Endpoint / payload / field map:** _(not started)_

### Arc (id=60, cat=B)
- **Official:** https://arc.dev/ · **Docs:** https://arc.dev/
- **Access mode:** partner_or_unknown · **Analysis:** TODO
- **Notes:** No verified public API.
- **Endpoint / payload / field map:** _(not started)_

### Gun.io (id=61, cat=B)
- **Official:** https://www.gun.io/ · **Docs:** https://www.gun.io/
- **Access mode:** partner_or_unknown · **Analysis:** TODO
- **Notes:** No verified public API.
- **Endpoint / payload / field map:** _(not started)_

### Wellfound (id=65, cat=B)
- **Official:** https://wellfound.com/ · **Docs:** https://wellfound.com/
- **Access mode:** unknown · **Analysis:** TODO
- **Notes:** Formerly AngelList; no verified open bulk API. Prefer free Jobicy/Himalayas/HN over paid scrapers.
- **Endpoint / payload / field map:** _(not started)_

### SAP SuccessFactors Recruiting (id=89, cat=D)
- **Official:** https://www.sap.com/ · **Docs:** https://www.sap.com/
- **Access mode:** enterprise · **Analysis:** TODO
- **Notes:** Enterprise OData; customer tenant credentials.
- **Endpoint / payload / field map:** _(not started)_

### Oracle Recruiting (id=90, cat=D)
- **Official:** https://www.oracle.com/ · **Docs:** https://www.oracle.com/
- **Access mode:** enterprise · **Analysis:** TODO
- **Notes:** Enterprise cloud credentials.
- **Endpoint / payload / field map:** _(not started)_

### iCIMS (id=91, cat=D)
- **Official:** https://www.icims.com/ · **Docs:** https://www.icims.com/
- **Access mode:** enterprise · **Analysis:** TODO
- **Notes:** Customer credentials.
- **Endpoint / payload / field map:** _(not started)_

### Open Exchange Rates (id=144, cat=G)
- **Official:** https://openexchangerates.org/ · **Docs:** https://docs.openexchangerates.org/
- **Access mode:** api_key · **Analysis:** TODO
- **Notes:** Optional FX overlay via OPEN_EXCHANGE_RATES_APP_ID on GET /api/v1/fx/rates; Frankfurter/ECB remain primary. Not a job connector.
- **Endpoint / payload / field map:** _(not started)_

### ExchangeRate-API (id=146, cat=G)
- **Official:** https://www.exchangerate-api.com/ · **Docs:** https://www.exchangerate-api.com/
- **Access mode:** api_key · **Analysis:** TODO
- **Notes:** API key required for production tiers.
- **Endpoint / payload / field map:** _(not started)_

### O*NET Web Services (id=150, cat=G)
- **Official:** https://services.onetcenter.org/ · **Docs:** https://services.onetcenter.org/
- **Access mode:** api_key · **Analysis:** TODO
- **Notes:** Registration required.
- **Endpoint / payload / field map:** _(not started)_

### Programmable Search Engine (id=165, cat=I)
- **Official:** https://programmablesearchengine.google.com/ · **Docs:** https://programmablesearchengine.google.com/
- **Access mode:** api_key · **Analysis:** TODO
- **Notes:** CSE for discovery; not a job board.
- **Endpoint / payload / field map:** _(not started)_

## Detail sheets — UNDER_REVIEW

Candidates without a wired connector. Prioritize by GEO/role needs before deep HTML analysis.

### Talent.com (id=14, cat=A)
- **Official:** https://www.talent.com/ · **Docs:** https://www.talent.com/
- **Access mode:** unknown · **Analysis:** TODO
- **Notes:** No verified public API docs in this pass.
- **Endpoint / payload / field map:** _(not started)_

### SimplyHired (id=15, cat=A)
- **Official:** https://www.simplyhired.com/ · **Docs:** https://www.simplyhired.com/
- **Access mode:** unknown · **Analysis:** TODO
- **Notes:** No verified public API in this pass.
- **Endpoint / payload / field map:** _(not started)_

### Totaljobs (id=18, cat=A)
- **Official:** https://www.totaljobs.com/ · **Docs:** https://www.totaljobs.com/
- **Access mode:** unknown · **Analysis:** TODO
- **Notes:** No verified public API in this pass.
- **Endpoint / payload / field map:** _(not started)_

### CV-Library (id=19, cat=A)
- **Official:** https://www.cv-library.co.uk/ · **Docs:** https://www.cv-library.co.uk/
- **Access mode:** unknown · **Analysis:** TODO
- **Notes:** No verified public API in this pass.
- **Endpoint / payload / field map:** _(not started)_

### CWJobs (id=20, cat=A)
- **Official:** https://www.cwjobs.co.uk/ · **Docs:** https://www.cwjobs.co.uk/
- **Access mode:** unknown · **Analysis:** TODO
- **Notes:** No verified public API in this pass.
- **Endpoint / payload / field map:** _(not started)_

### Technojobs (id=21, cat=A)
- **Official:** https://www.technojobs.co.uk/ · **Docs:** https://www.technojobs.co.uk/
- **Access mode:** unknown · **Analysis:** TODO
- **Notes:** No verified public API in this pass.
- **Endpoint / payload / field map:** _(not started)_

### Welcome to the Jungle (id=22, cat=A)
- **Official:** https://www.welcometothejungle.com/ · **Docs:** https://www.welcometothejungle.com/
- **Access mode:** unknown · **Analysis:** TODO
- **Notes:** No verified public bulk API in this pass.
- **Endpoint / payload / field map:** _(not started)_

### jobs.ch (id=26, cat=A)
- **Official:** https://www.jobs.ch/ · **Docs:** https://www.jobs.ch/
- **Access mode:** unknown · **Analysis:** TODO
- **Notes:** No verified public API in this pass.
- **Endpoint / payload / field map:** _(not started)_

### JobScout24 (id=27, cat=A)
- **Official:** https://www.jobscout24.ch/ · **Docs:** https://www.jobscout24.ch/
- **Access mode:** unknown · **Analysis:** TODO
- **Notes:** No verified public API in this pass.
- **Endpoint / payload / field map:** _(not started)_

### APEC (id=32, cat=A)
- **Official:** https://www.apec.fr/ · **Docs:** https://www.apec.fr/
- **Access mode:** unknown · **Analysis:** TODO
- **Notes:** No verified public bulk API in this pass.
- **Endpoint / payload / field map:** _(not started)_

### VDAB (id=33, cat=A)
- **Official:** https://www.vdab.be/ · **Docs:** https://www.vdab.be/
- **Access mode:** unknown · **Analysis:** TODO
- **Notes:** May offer open data; not validated this pass.
- **Endpoint / payload / field map:** _(not started)_

### Actiris (id=34, cat=A)
- **Official:** https://www.actiris.brussels/ · **Docs:** https://www.actiris.brussels/
- **Access mode:** unknown · **Analysis:** TODO
- **Notes:** Not validated this pass.
- **Endpoint / payload / field map:** _(not started)_

### Nationale Vacaturebank (id=36, cat=A)
- **Official:** https://www.nationalevacaturebank.nl/ · **Docs:** https://www.nationalevacaturebank.nl/
- **Access mode:** unknown · **Analysis:** TODO
- **Notes:** No verified public job API this pass. NL listings: findmethatdamjob (public API) or Adzuna nl when keyed — not Werk.nl scrape.
- **Endpoint / payload / field map:** _(not started)_

### IrishJobs (id=37, cat=A)
- **Official:** https://www.irishjobs.ie/ · **Docs:** https://www.irishjobs.ie/
- **Access mode:** unknown · **Analysis:** TODO
- **Notes:** Not validated this pass.
- **Endpoint / payload / field map:** _(not started)_

### Pracuj.pl (id=38, cat=A)
- **Official:** https://www.pracuj.pl/ · **Docs:** https://www.pracuj.pl/
- **Access mode:** unknown · **Analysis:** TODO
- **Notes:** Not validated this pass.
- **Endpoint / payload / field map:** _(not started)_

### Jobly (id=39, cat=A)
- **Official:** https://www.jobly.fi/ · **Docs:** https://www.jobly.fi/
- **Access mode:** unknown · **Analysis:** TODO
- **Notes:** Not validated this pass.
- **Endpoint / payload / field map:** _(not started)_

### Malt (id=43, cat=B)
- **Official:** https://www.malt.com/ · **Docs:** https://www.malt.com/
- **Access mode:** partner_or_unknown · **Analysis:** TODO
- **Notes:** Official integration / export only.
- **Endpoint / payload / field map:** _(not started)_

### Flexiple (id=66, cat=B)
- **Official:** https://flexiple.com/ · **Docs:** https://flexiple.com/
- **Access mode:** unknown · **Analysis:** TODO
- **Notes:** No verified public API.
- **Endpoint / payload / field map:** _(not started)_

### Hays (id=67, cat=C)
- **Official:** https://www.hays.com/ · **Docs:** https://www.hays.com/
- **Access mode:** website_or_feed · **Analysis:** TODO
- **Notes:** Agency site; no verified public bulk API. Prefer ATS board APIs or lawful import.
- **Endpoint / payload / field map:** _(not started)_

### Michael Page (id=68, cat=C)
- **Official:** https://www.michaelpage.com/ · **Docs:** https://www.michaelpage.com/
- **Access mode:** website_or_feed · **Analysis:** TODO
- **Notes:** Agency site; no verified public bulk API. Prefer ATS board APIs or lawful import.
- **Endpoint / payload / field map:** _(not started)_

### Robert Half (id=69, cat=C)
- **Official:** https://www.roberthalf.com/ · **Docs:** https://www.roberthalf.com/
- **Access mode:** website_or_feed · **Analysis:** TODO
- **Notes:** Agency site; no verified public bulk API. Prefer ATS board APIs or lawful import.
- **Endpoint / payload / field map:** _(not started)_

### Randstad (id=70, cat=C)
- **Official:** https://www.randstad.com/ · **Docs:** https://www.randstad.com/
- **Access mode:** website_or_feed · **Analysis:** TODO
- **Notes:** Agency site; no verified public bulk API. Prefer ATS board APIs or lawful import.
- **Endpoint / payload / field map:** _(not started)_

### Adecco (id=71, cat=C)
- **Official:** https://www.adecco.com/ · **Docs:** https://www.adecco.com/
- **Access mode:** website_or_feed · **Analysis:** TODO
- **Notes:** Agency site; no verified public bulk API. Prefer ATS board APIs or lawful import.
- **Endpoint / payload / field map:** _(not started)_

### Manpower (id=72, cat=C)
- **Official:** https://www.manpower.com/ · **Docs:** https://www.manpower.com/
- **Access mode:** website_or_feed · **Analysis:** TODO
- **Notes:** Agency site; no verified public bulk API. Prefer ATS board APIs or lawful import.
- **Endpoint / payload / field map:** _(not started)_

### Experis (id=73, cat=C)
- **Official:** https://www.experis.com/ · **Docs:** https://www.experis.com/
- **Access mode:** website_or_feed · **Analysis:** TODO
- **Notes:** Agency site; no verified public bulk API. Prefer ATS board APIs or lawful import.
- **Endpoint / payload / field map:** _(not started)_

### TEKsystems (id=74, cat=C)
- **Official:** https://www.teksystems.com/ · **Docs:** https://www.teksystems.com/
- **Access mode:** website_or_feed · **Analysis:** TODO
- **Notes:** Agency site; no verified public bulk API. Prefer ATS board APIs or lawful import.
- **Endpoint / payload / field map:** _(not started)_

### Kforce (id=75, cat=C)
- **Official:** https://www.kforce.com/ · **Docs:** https://www.kforce.com/
- **Access mode:** website_or_feed · **Analysis:** TODO
- **Notes:** Agency site; no verified public bulk API. Prefer ATS board APIs or lawful import.
- **Endpoint / payload / field map:** _(not started)_

### Robert Walters (id=76, cat=C)
- **Official:** https://www.robertwalters.com/ · **Docs:** https://www.robertwalters.com/
- **Access mode:** website_or_feed · **Analysis:** TODO
- **Notes:** Agency site; no verified public bulk API. Prefer ATS board APIs or lawful import.
- **Endpoint / payload / field map:** _(not started)_

### Harvey Nash (id=77, cat=C)
- **Official:** https://www.harveynash.com/ · **Docs:** https://www.harveynash.com/
- **Access mode:** website_or_feed · **Analysis:** TODO
- **Notes:** Agency site; no verified public bulk API. Prefer ATS board APIs or lawful import.
- **Endpoint / payload / field map:** _(not started)_

### Computer Futures (id=78, cat=C)
- **Official:** https://www.computerfutures.com/ · **Docs:** https://www.computerfutures.com/
- **Access mode:** website_or_feed · **Analysis:** TODO
- **Notes:** Agency site; no verified public bulk API. Prefer ATS board APIs or lawful import.
- **Endpoint / payload / field map:** _(not started)_

### Nigel Frank (id=79, cat=C)
- **Official:** https://www.nigelfrank.com/ · **Docs:** https://www.nigelfrank.com/
- **Access mode:** website_or_feed · **Analysis:** TODO
- **Notes:** Agency site; no verified public bulk API. Prefer ATS board APIs or lawful import.
- **Endpoint / payload / field map:** _(not started)_

### Huxley (id=80, cat=C)
- **Official:** https://www.huxley.com/ · **Docs:** https://www.huxley.com/
- **Access mode:** website_or_feed · **Analysis:** TODO
- **Notes:** Agency site; no verified public bulk API. Prefer ATS board APIs or lawful import.
- **Endpoint / payload / field map:** _(not started)_

### La Fosse (id=81, cat=C)
- **Official:** https://www.lafosse.com/ · **Docs:** https://www.lafosse.com/
- **Access mode:** website_or_feed · **Analysis:** TODO
- **Notes:** Agency site; no verified public bulk API. Prefer ATS board APIs or lawful import.
- **Endpoint / payload / field map:** _(not started)_

### Brio Digital (id=82, cat=C)
- **Official:** https://www.briodigital.io/ · **Docs:** https://www.briodigital.io/
- **Access mode:** website_or_feed · **Analysis:** TODO
- **Notes:** Agency site; no verified public bulk API. Prefer ATS board APIs or lawful import.
- **Endpoint / payload / field map:** _(not started)_

### BambooHR public careers (id=95, cat=D)
- **Official:** https://www.bamboohr.com/ · **Docs:** https://documentation.bamboohr.com/reference/applicant-tracking
- **Access mode:** public_api_per_company · **Analysis:** TODO
- **Notes:** Collector wired: GET {slug}.bamboohr.com/careers/list (+ optional /detail). BAMBOOHR_COMPANIES default flyio (200+jobs probed 2026-10-21); DC egress may still 503 — re-probe before expanding; promote ACTIVE after live inserts. Open API ATS remains credentialed/PARTNER.
- **Endpoint / payload / field map:** _(not started)_

### Cedefop Skills-OVATE (id=98, cat=E)
- **Official:** https://www.cedefop.europa.eu/en/tools/skills-online-vacancies · **Docs:** https://www.cedefop.europa.eu/en/tools/skills-online-vacancies
- **Access mode:** portal · **Analysis:** TODO
- **Notes:** Official statistics — import via datasets/API; do not mix incomparable series. Not wired as job connector.
- **Endpoint / payload / field map:** _(not started)_

### OECD Data (id=100, cat=E)
- **Official:** https://data.oecd.org/ · **Docs:** https://data.oecd.org/
- **Access mode:** open_data · **Analysis:** TODO
- **Notes:** Official statistics — import via datasets/API; do not mix incomparable series. Not wired as job connector.
- **Endpoint / payload / field map:** _(not started)_

### ILOSTAT (id=101, cat=E)
- **Official:** https://ilostat.ilo.org/ · **Docs:** https://ilostat.ilo.org/
- **Access mode:** open_data · **Analysis:** TODO
- **Notes:** Official statistics — import via datasets/API; do not mix incomparable series. Not wired as job connector.
- **Endpoint / payload / field map:** _(not started)_

### World Bank Data (id=102, cat=E)
- **Official:** https://data.worldbank.org/ · **Docs:** https://data.worldbank.org/
- **Access mode:** open_data · **Analysis:** TODO
- **Notes:** Official statistics — import via datasets/API; do not mix incomparable series. Not wired as job connector.
- **Endpoint / payload / field map:** _(not started)_

### IMF Data (id=103, cat=E)
- **Official:** https://www.imf.org/en/Data · **Docs:** https://www.imf.org/en/Data
- **Access mode:** open_data · **Analysis:** TODO
- **Notes:** Official statistics — import via datasets/API; do not mix incomparable series. Not wired as job connector.
- **Endpoint / payload / field map:** _(not started)_

### UN Data (id=104, cat=E)
- **Official:** https://data.un.org/ · **Docs:** https://data.un.org/
- **Access mode:** open_data · **Analysis:** TODO
- **Notes:** Official statistics — import via datasets/API; do not mix incomparable series. Not wired as job connector.
- **Endpoint / payload / field map:** _(not started)_

### US Bureau of Labor Statistics (id=105, cat=E)
- **Official:** https://www.bls.gov/data/ · **Docs:** https://www.bls.gov/data/
- **Access mode:** api_key_optional · **Analysis:** TODO
- **Notes:** Official statistics — import via datasets/API; do not mix incomparable series. Not wired as job connector.
- **Endpoint / payload / field map:** _(not started)_

### US Census Bureau (id=106, cat=E)
- **Official:** https://www.census.gov/data.html · **Docs:** https://www.census.gov/data.html
- **Access mode:** api_key · **Analysis:** TODO
- **Notes:** Official statistics — import via datasets/API; do not mix incomparable series. Not wired as job connector.
- **Endpoint / payload / field map:** _(not started)_

### US O*NET (id=107, cat=E)
- **Official:** https://www.onetonline.org/ · **Docs:** https://www.onetonline.org/
- **Access mode:** api_key · **Analysis:** TODO
- **Notes:** Official statistics — import via datasets/API; do not mix incomparable series. Not wired as job connector.
- **Endpoint / payload / field map:** _(not started)_

### Statistics Canada (id=109, cat=E)
- **Official:** https://www.statcan.gc.ca/ · **Docs:** https://www.statcan.gc.ca/
- **Access mode:** open_data · **Analysis:** TODO
- **Notes:** Official statistics — import via datasets/API; do not mix incomparable series. Not wired as job connector.
- **Endpoint / payload / field map:** _(not started)_

### Australian Bureau of Statistics (id=110, cat=E)
- **Official:** https://www.abs.gov.au/ · **Docs:** https://www.abs.gov.au/
- **Access mode:** open_data · **Analysis:** TODO
- **Notes:** Official statistics — import via datasets/API; do not mix incomparable series. Not wired as job connector.
- **Endpoint / payload / field map:** _(not started)_

### Australian Labour Market Insights (id=111, cat=E)
- **Official:** https://labourmarketinsights.gov.au/ · **Docs:** https://labourmarketinsights.gov.au/
- **Access mode:** portal · **Analysis:** TODO
- **Notes:** Official statistics — import via datasets/API; do not mix incomparable series. Not wired as job connector.
- **Endpoint / payload / field map:** _(not started)_

### Statistics New Zealand (id=112, cat=E)
- **Official:** https://www.stats.govt.nz/ · **Docs:** https://www.stats.govt.nz/
- **Access mode:** open_data · **Analysis:** TODO
- **Notes:** Official statistics — import via datasets/API; do not mix incomparable series. Not wired as job connector.
- **Endpoint / payload / field map:** _(not started)_

### Swiss Federal Statistical Office (id=113, cat=E)
- **Official:** https://www.bfs.admin.ch/ · **Docs:** https://www.bfs.admin.ch/
- **Access mode:** open_data · **Analysis:** TODO
- **Notes:** Official statistics — import via datasets/API; do not mix incomparable series. Not wired as job connector.
- **Endpoint / payload / field map:** _(not started)_

### Salarium Switzerland (id=114, cat=E)
- **Official:** https://www.salarium.bfs.admin.ch/ · **Docs:** https://www.salarium.bfs.admin.ch/
- **Access mode:** portal · **Analysis:** TODO
- **Notes:** Official statistics — import via datasets/API; do not mix incomparable series. Not wired as job connector.
- **Endpoint / payload / field map:** _(not started)_

### SECO Switzerland (id=115, cat=E)
- **Official:** https://www.seco.admin.ch/ · **Docs:** https://www.seco.admin.ch/
- **Access mode:** portal · **Analysis:** TODO
- **Notes:** Official statistics — import via datasets/API; do not mix incomparable series. Not wired as job connector.
- **Endpoint / payload / field map:** _(not started)_

### ISTAT (id=116, cat=E)
- **Official:** https://www.istat.it/ · **Docs:** https://www.istat.it/
- **Access mode:** open_data · **Analysis:** TODO
- **Notes:** Official statistics — import via datasets/API; do not mix incomparable series. Not wired as job connector.
- **Endpoint / payload / field map:** _(not started)_

### INPS (id=117, cat=E)
- **Official:** https://www.inps.it/ · **Docs:** https://www.inps.it/
- **Access mode:** portal · **Analysis:** TODO
- **Notes:** Official statistics — import via datasets/API; do not mix incomparable series. Not wired as job connector.
- **Endpoint / payload / field map:** _(not started)_

### Unioncamere Excelsior (id=118, cat=E)
- **Official:** https://excelsior.unioncamere.net/ · **Docs:** https://excelsior.unioncamere.net/
- **Access mode:** portal · **Analysis:** TODO
- **Notes:** Official statistics — import via datasets/API; do not mix incomparable series. Not wired as job connector.
- **Endpoint / payload / field map:** _(not started)_

### Ministero del Lavoro IT (id=119, cat=E)
- **Official:** https://www.lavoro.gov.it/ · **Docs:** https://www.lavoro.gov.it/
- **Access mode:** portal · **Analysis:** TODO
- **Notes:** Official statistics — import via datasets/API; do not mix incomparable series. Not wired as job connector.
- **Endpoint / payload / field map:** _(not started)_

### UK ONS (id=122, cat=E)
- **Official:** https://www.ons.gov.uk/ · **Docs:** https://www.ons.gov.uk/
- **Access mode:** open_data · **Analysis:** TODO
- **Notes:** Official statistics — import via datasets/API; do not mix incomparable series. Not wired as job connector.
- **Endpoint / payload / field map:** _(not started)_

### UK National Careers Service (id=123, cat=E)
- **Official:** https://nationalcareers.service.gov.uk/ · **Docs:** https://nationalcareers.service.gov.uk/
- **Access mode:** portal · **Analysis:** TODO
- **Notes:** Official statistics — import via datasets/API; do not mix incomparable series. Not wired as job connector.
- **Endpoint / payload / field map:** _(not started)_

### Statistics Netherlands (id=124, cat=E)
- **Official:** https://www.cbs.nl/ · **Docs:** https://www.cbs.nl/
- **Access mode:** open_data · **Analysis:** TODO
- **Notes:** Official statistics — import via datasets/API; do not mix incomparable series. Not wired as job connector.
- **Endpoint / payload / field map:** _(not started)_

### Statistics Norway (id=125, cat=E)
- **Official:** https://www.ssb.no/ · **Docs:** https://www.ssb.no/
- **Access mode:** open_data · **Analysis:** TODO
- **Notes:** Official statistics — import via datasets/API; do not mix incomparable series. Not wired as job connector.
- **Endpoint / payload / field map:** _(not started)_

### Statistics Sweden (id=126, cat=E)
- **Official:** https://www.scb.se/ · **Docs:** https://www.scb.se/
- **Access mode:** open_data · **Analysis:** TODO
- **Notes:** Official statistics — import via datasets/API; do not mix incomparable series. Not wired as job connector.
- **Endpoint / payload / field map:** _(not started)_

### Statistics Finland (id=127, cat=E)
- **Official:** https://stat.fi/ · **Docs:** https://stat.fi/
- **Access mode:** open_data · **Analysis:** TODO
- **Notes:** Official statistics — import via datasets/API; do not mix incomparable series. Not wired as job connector.
- **Endpoint / payload / field map:** _(not started)_

### Statistics Denmark (id=128, cat=E)
- **Official:** https://www.dst.dk/ · **Docs:** https://www.dst.dk/
- **Access mode:** open_data · **Analysis:** TODO
- **Notes:** Official statistics — import via datasets/API; do not mix incomparable series. Not wired as job connector.
- **Endpoint / payload / field map:** _(not started)_

### Statistics Poland (id=129, cat=E)
- **Official:** https://stat.gov.pl/ · **Docs:** https://stat.gov.pl/
- **Access mode:** open_data · **Analysis:** TODO
- **Notes:** Official statistics — import via datasets/API; do not mix incomparable series. Not wired as job connector.
- **Endpoint / payload / field map:** _(not started)_

### Stack Overflow Developer Survey (id=131, cat=F)
- **Official:** https://survey.stackoverflow.co/ · **Docs:** https://survey.stackoverflow.co/
- **Access mode:** report_or_dataset · **Analysis:** TODO
- **Notes:** Survey/report — use lawful download/import; do not scrape paywalled pages. Not a live job connector.
- **Endpoint / payload / field map:** _(not started)_

### JetBrains Developer Ecosystem (id=132, cat=F)
- **Official:** https://www.jetbrains.com/lp/devecosystem/ · **Docs:** https://www.jetbrains.com/lp/devecosystem/
- **Access mode:** report_or_dataset · **Analysis:** TODO
- **Notes:** Survey/report — use lawful download/import; do not scrape paywalled pages. Not a live job connector.
- **Endpoint / payload / field map:** _(not started)_

### GitHub Octoverse (id=133, cat=F)
- **Official:** https://github.blog/news-insights/octoverse/ · **Docs:** https://github.blog/news-insights/octoverse/
- **Access mode:** report_or_dataset · **Analysis:** TODO
- **Notes:** Survey/report — use lawful download/import; do not scrape paywalled pages. Not a live job connector.
- **Endpoint / payload / field map:** _(not started)_

### CNCF Reports (id=134, cat=F)
- **Official:** https://www.cncf.io/reports/ · **Docs:** https://www.cncf.io/reports/
- **Access mode:** report_or_dataset · **Analysis:** TODO
- **Notes:** Survey/report — use lawful download/import; do not scrape paywalled pages. Not a live job connector.
- **Endpoint / payload / field map:** _(not started)_

### DORA (id=135, cat=F)
- **Official:** https://dora.dev/ · **Docs:** https://dora.dev/
- **Access mode:** report_or_dataset · **Analysis:** TODO
- **Notes:** Survey/report — use lawful download/import; do not scrape paywalled pages. Not a live job connector.
- **Endpoint / payload / field map:** _(not started)_

### Levels.fyi (id=136, cat=F)
- **Official:** https://www.levels.fyi/ · **Docs:** https://www.levels.fyi/
- **Access mode:** report_or_dataset · **Analysis:** TODO
- **Notes:** Survey/report — use lawful download/import; do not scrape paywalled pages. Not a live job connector.
- **Endpoint / payload / field map:** _(not started)_

### Glassdoor (id=137, cat=F)
- **Official:** https://www.glassdoor.com/ · **Docs:** https://www.glassdoor.com/
- **Access mode:** report_or_dataset · **Analysis:** TODO
- **Notes:** Survey/report — use lawful download/import; do not scrape paywalled pages. Not a live job connector.
- **Endpoint / payload / field map:** _(not started)_

### PayScale (id=138, cat=F)
- **Official:** https://www.payscale.com/ · **Docs:** https://www.payscale.com/
- **Access mode:** report_or_dataset · **Analysis:** TODO
- **Notes:** Survey/report — use lawful download/import; do not scrape paywalled pages. Not a live job connector.
- **Endpoint / payload / field map:** _(not started)_

### Salary.com (id=139, cat=F)
- **Official:** https://www.salary.com/ · **Docs:** https://www.salary.com/
- **Access mode:** report_or_dataset · **Analysis:** TODO
- **Notes:** Survey/report — use lawful download/import; do not scrape paywalled pages. Not a live job connector.
- **Endpoint / payload / field map:** _(not started)_

### Hays Salary Guides (id=140, cat=F)
- **Official:** https://www.hays.com/salary-guide · **Docs:** https://www.hays.com/salary-guide
- **Access mode:** report_or_dataset · **Analysis:** TODO
- **Notes:** Survey/report — use lawful download/import; do not scrape paywalled pages. Not a live job connector.
- **Endpoint / payload / field map:** _(not started)_

### Robert Half Salary Guides (id=141, cat=F)
- **Official:** https://www.roberthalf.com/salary-guide · **Docs:** https://www.roberthalf.com/salary-guide
- **Access mode:** report_or_dataset · **Analysis:** TODO
- **Notes:** Survey/report — use lawful download/import; do not scrape paywalled pages. Not a live job connector.
- **Endpoint / payload / field map:** _(not started)_

### Michael Page Salary Guides (id=142, cat=F)
- **Official:** https://www.michaelpage.com/salary-guide · **Docs:** https://www.michaelpage.com/salary-guide
- **Access mode:** report_or_dataset · **Analysis:** TODO
- **Notes:** Survey/report — use lawful download/import; do not scrape paywalled pages. Not a live job connector.
- **Endpoint / payload / field map:** _(not started)_

### TED (id=151, cat=H)
- **Official:** https://ted.europa.eu/ · **Docs:** https://ted.europa.eu/
- **Access mode:** open_data_or_portal · **Analysis:** TODO
- **Notes:** Procurement ≠ job postings. Separate ingest path Later; contract value ≠ day rate.
- **Endpoint / payload / field map:** _(not started)_

### EU Funding & Tenders Portal (id=152, cat=H)
- **Official:** https://ec.europa.eu/info/funding-tenders/opportunities/portal/ · **Docs:** https://ec.europa.eu/info/funding-tenders/opportunities/portal/
- **Access mode:** open_data_or_portal · **Analysis:** TODO
- **Notes:** Procurement ≠ job postings. Separate ingest path Later; contract value ≠ day rate.
- **Endpoint / payload / field map:** _(not started)_

### UK Contracts Finder (id=153, cat=H)
- **Official:** https://www.contractsfinder.service.gov.uk/ · **Docs:** https://www.contractsfinder.service.gov.uk/
- **Access mode:** open_data_or_portal · **Analysis:** TODO
- **Notes:** Procurement ≠ job postings. Separate ingest path Later; contract value ≠ day rate.
- **Endpoint / payload / field map:** _(not started)_

### UK Find a Tender (id=154, cat=H)
- **Official:** https://www.find-tender.service.gov.uk/ · **Docs:** https://www.find-tender.service.gov.uk/
- **Access mode:** open_data_or_portal · **Analysis:** TODO
- **Notes:** Procurement ≠ job postings. Separate ingest path Later; contract value ≠ day rate.
- **Endpoint / payload / field map:** _(not started)_

### US SAM.gov (id=155, cat=H)
- **Official:** https://sam.gov/ · **Docs:** https://sam.gov/
- **Access mode:** open_data_or_portal · **Analysis:** TODO
- **Notes:** Procurement ≠ job postings. Separate ingest path Later; contract value ≠ day rate.
- **Endpoint / payload / field map:** _(not started)_

### US FPDS (id=156, cat=H)
- **Official:** https://www.fpds.gov/ · **Docs:** https://www.fpds.gov/
- **Access mode:** open_data_or_portal · **Analysis:** TODO
- **Notes:** Procurement ≠ job postings. Separate ingest path Later; contract value ≠ day rate.
- **Endpoint / payload / field map:** _(not started)_

### US GSA eBuy (id=157, cat=H)
- **Official:** https://www.gsa.gov/ · **Docs:** https://www.gsa.gov/
- **Access mode:** open_data_or_portal · **Analysis:** TODO
- **Notes:** Procurement ≠ job postings. Separate ingest path Later; contract value ≠ day rate.
- **Endpoint / payload / field map:** _(not started)_

### CanadaBuys (id=158, cat=H)
- **Official:** https://canadabuys.canada.ca/ · **Docs:** https://canadabuys.canada.ca/
- **Access mode:** open_data_or_portal · **Analysis:** TODO
- **Notes:** Procurement ≠ job postings. Separate ingest path Later; contract value ≠ day rate.
- **Endpoint / payload / field map:** _(not started)_

### AusTender (id=159, cat=H)
- **Official:** https://www.tenders.gov.au/ · **Docs:** https://www.tenders.gov.au/
- **Access mode:** open_data_or_portal · **Analysis:** TODO
- **Notes:** Procurement ≠ job postings. Separate ingest path Later; contract value ≠ day rate.
- **Endpoint / payload / field map:** _(not started)_

### Swiss SIMAP (id=160, cat=H)
- **Official:** https://www.simap.ch/ · **Docs:** https://www.simap.ch/
- **Access mode:** open_data_or_portal · **Analysis:** TODO
- **Notes:** Procurement ≠ job postings. Separate ingest path Later; contract value ≠ day rate.
- **Endpoint / payload / field map:** _(not started)_

### Open Contracting Data Standard (id=161, cat=H)
- **Official:** https://standard.open-contracting.org/ · **Docs:** https://standard.open-contracting.org/
- **Access mode:** open_data_or_portal · **Analysis:** TODO
- **Notes:** Procurement ≠ job postings. Separate ingest path Later; contract value ≠ day rate.
- **Endpoint / payload / field map:** _(not started)_

### Open Contracting Partnership (id=162, cat=H)
- **Official:** https://www.open-contracting.org/ · **Docs:** https://www.open-contracting.org/
- **Access mode:** open_data_or_portal · **Analysis:** TODO
- **Notes:** Procurement ≠ job postings. Separate ingest path Later; contract value ≠ day rate.
- **Endpoint / payload / field map:** _(not started)_

### Internet Archive (id=167, cat=I)
- **Official:** https://archive.org/ · **Docs:** https://archive.org/
- **Access mode:** api · **Analysis:** TODO
- **Notes:** Historical pages; not primary live jobs.
- **Endpoint / payload / field map:** _(not started)_

## DISCOVERED / REJECTED

- **Google for Jobs** (id=13, `REJECTED`) — Analysis: SKIP. dup_of=None · Structured data for employers publishing jobs to Google; not a job-search API for bulk pull.
- **No Fluff Jobs** (id=23, `DISCOVERED`) — Analysis: SKIP. dup_of=176 · Duplicate of catalog_id 176 (NoFluffJobs ACTIVE connector).
- **InfoJobs Spain** (id=42, `DISCOVERED`) — Analysis: SKIP. dup_of=25 · Duplicate of catalog_id 25 (same domain).
- **ESCO** (id=99, `DISCOVERED`) — Analysis: SKIP. dup_of=149 · Duplicate of catalog_id 149 (ESCO API taxonomy helper).
- **USAJOBS (stats ref)** (id=108, `DISCOVERED`) — Analysis: SKIP. dup_of=7 · Duplicate reference of catalog_id 7.
- **Bundesagentur für Arbeit (stats)** (id=120, `DISCOVERED`) — Analysis: SKIP. dup_of=30 · Duplicate reference of catalog_id 30.
- **France Travail (stats)** (id=121, `DISCOVERED`) — Analysis: SKIP. dup_of=31 · Duplicate reference of catalog_id 31.
- **Stats NZ** (id=130, `DISCOVERED`) — Analysis: SKIP. dup_of=112 · Duplicate reference of catalog_id 112.
- **Common Crawl** (id=166, `REJECTED`) — Analysis: SKIP. dup_of=None · Not authorized job harvest path for FMI; ToS/use-case mismatch.
- **Google Job Posting docs** (id=169, `DISCOVERED`) — Analysis: SKIP. dup_of=13 · Same as catalog_id 13.

