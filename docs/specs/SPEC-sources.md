# Spec: sources (global catalog & verification)

## Objective

Maintain a worldwide, continuously expandable registry of IT / freelance / contractor data sources (~193 catalog entries), with honest verification statuses, modular connectors only where legally and technically accessible, and clear gaps for credentials or non-automatable paths.

Aligns with the global sources integration prompt (categories A–I). Detailed evidence: [../sources/VALIDATION_REPORT.md](../sources/VALIDATION_REPORT.md), catalog [`../../data/sources/catalog.json`](../../data/sources/catalog.json).

## Priority market

Professions (observed demand, not invented totals):

- Senior Java / Spring Boot, Backend / Full-Stack, Cloud / Platform / DevOps
- Architect / Tech Lead, AI / GenAI / LLM / RAG / Agents, Data / ML
- Freelance IT Consultant / Independent Contractor, Enterprise AI Architect

Geography: **worldwide** (source-biased; remote boards currently over-represented — see [../sources/COVERAGE_GAPS.md](../sources/COVERAGE_GAPS.md)).

## Categories (catalog)

| Id | Category |
|----|----------|
| A | Job aggregators / search APIs |
| B | Freelance / contractor marketplaces |
| C | Recruiting agencies |
| D | Public ATS board APIs |
| E | Official labour / wage statistics |
| F | Salary surveys / tech reports |
| G | FX, ISO codes, taxonomies (ESCO, JobTech, O*NET) |
| H | Public procurement |
| I | Discovery support (directories, schema) |

## Verification statuses

`DISCOVERED` · `UNDER_REVIEW` · `NEEDS_CREDENTIALS` · `PENDING_ACCESS` · `VALIDATED` · `IMPLEMENTED` · `ACTIVE` · `DEGRADED` · `BLOCKED` · `DEPRECATED` · `REJECTED`

**Rule:** `ACTIVE` only after a connector in this repo returns real records under automated or manual live test. Never invent credentials success, licenses, or costs.

## Mandatory procedure (per source)

1. Open official URL · 2. Confirm domain · 3. Find API/feed/dataset docs · 4. Fields · 5. Geo/languages · 6. Auth/quotas/cost · 7. License · 8. Authorized automation? · 9. Non-destructive probe · 10. Save evidence · 11. Implement if usable · 12. Automated tests · 13. Record gaps

Regenerate catalog: `python3 backend/scripts/generate_source_catalog.py`

## In scope (shipped)

- Catalog JSON + seed sync into `sources` (+ `verification_status`, `catalog_id`, `category`, `source_verifications` table).
- ACTIVE job connectors: Remotive, Arbeitnow, Remote OK, Working Nomads, We Work Remotely, The Muse, Jobicy, Himalayas, HN Who is hiring (Algolia), DevITJobs, NoFluffJobs, Reed (RSS), Get on Board, MyCareersFuture, JobUp, NAV Arbeidsplassen, Landing.jobs, okemprego (PT `it-data` default), Canada Job Bank open data (`jobbank_ca`), Kalibrr, DOU.ua, Authentic Jobs, Wantedly, Duunitori, Jobindex, Wanted, Instahyre, Hasjob, HelloWorld.rs, Posao.hr, Jobweb Kenya, Dev Global Jobs (LU/BG default), ViewJobs (AU MCP), Greenhouse/Lever/Ashby/SmartRecruiters (configured tenants), Arbetsförmedlingen JobSearch, manual import.
- Prefer free public APIs/RSS over paid aggregator APIs ([ADR-003](../decisions/ADR-003-authorized-connectors-only.md)); never scrape paywalled/login sites.
- Credentialed scaffolds (fail closed; catalog stays `NEEDS_CREDENTIALS` until live): Adzuna, USAJOBS, France Travail, Bundesagentur, Jooble — see [../sources/CREDENTIALED_CONNECTORS.md](../sources/CREDENTIALED_CONNECTORS.md); `GET /api/v1/ops/connectors`; promote via `scripts/promote_source_active.py`.
- FX helpers: Frankfurter, ECB (`GET /api/v1/fx/rates`).
- Taxonomy helpers (reference only): ESCO, JobTech Taxonomy (`/api/v1/taxonomy/.../search`).
- Stats helper (reference only): Eurostat allowlisted series (`/api/v1/stats/eurostat/series`).
- APIs: `/api/v1/sources`, `/sources/catalog`, `/sources/catalog/summary`.
- Sources dashboard (runnable vs catalog + credentialed scaffold status).
- Live collector tests + catalog API tests.

## Out of scope until credentials / Later

- Indeed, LinkedIn, Malt, Upwork, etc. (still no scaffold / partner path).
- Promoting credentialed scaffolds to `ACTIVE` without operator live ingest.
- Scraping behind login/CAPTCHA/paywall/ToS.
- Treating Google for Jobs / Common Crawl as pull job APIs (`REJECTED`).
- Mixing incomparable national statistics series into job KPIs.
- Equating procurement contract value to day rates.

## Acceptance criteria

- [x] Catalog covers prompt entries with duplicates marked (`duplicate_of`).
- [x] ACTIVE connectors have live tests or smoke evidence.
- [x] UI/API expose verification status; non-runnable sources cannot be “faked” as integrated.
- [x] Coverage gaps documented.
- [x] Credentialed scaffolds implemented fail-closed; ACTIVE only after real keys + live evidence (gate enforced in seed).
- [x] Eurostat allowlisted series helper (reference only; not job ingest).
- [ ] Broader stats (E), surveys (F), procurement (H) ingest paths when prioritized (Later).

## Key paths

- `data/sources/catalog.json`
- `backend/scripts/generate_source_catalog.py`
- `backend/app/sources/catalog.py`
- `backend/app/collectors/`
- `backend/app/fx/rates.py`
- `docs/sources/`
