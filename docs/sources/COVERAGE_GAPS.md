# Coverage gaps

Evidence-first: gaps are about **observed source coverage**, not total market size. Product priority roles and worldwide scope: [../PRODUCT.md](../PRODUCT.md). Expansion plan: [../superpowers/plans/2026-10-20-global-sources.md](../superpowers/plans/2026-10-20-global-sources.md).

## Geographic

| Region | Live job connectors today | Gap |
|--------|---------------------------|-----|
| Global remote | Remotive, Remote OK, WWR, Working Nomads, The Muse, Jobicy, Himalayas, HN Who is hiring, DevITJobs | Strong remote bias; free boards preferred over paid aggregators |
| Australia | ViewJobs (`viewjobs`) MCP search | Dedicated free AU path; Seek remains partner-only / no public search API |
| EU DE-heavy | Arbeitnow + Bundesagentur scaffold | BA Jobsuche not ACTIVE until keyed live run |
| CEE / PL | NoFluffJobs (`nofluffjobs`) | Strong IT + frequent B2B hourly; full dump is heavy |
| UK IT | DevITJobs UK + Reed RSS (`reed`) | Optional Reed API key for richer JSON fields |
| Nordics SE / NO / FI / DK | Arbetsförmedlingen + NAV + Duunitori (`duunitori`) + Jobindex (`jobindex`) | Official FI/DK PES still gaps; commercial boards ACTIVE |
| US federal | USAJOBS scaffold (`USAJOBS_*` keys) | Not ACTIVE until live run with key + User-Agent email |
| Canada | Job Bank open data (`jobbank_ca`) | Monthly ESDC CSV (OGL); IT via NOC21; complements remote/ATS for CA private market |
| UK | Adzuna scaffold + Reed RSS ACTIVE | Find a Job DWP still under review; Adzuna ACTIVE only after keyed live run |
| FR | France Travail scaffold | OAuth client credentials; ACTIVE only after live |
| CH | JobUp (`jobup`) public search | BE / NL PES still gaps |
| LATAM | Get on Board (`getonbrd`) | Strong remote LATAM IT |
| APAC SG / SEA / JP / KR / IN | MyCareersFuture + Kalibrr + Wantedly + Wanted (`wanted`) + Instahyre (`instahyre`) + Hasjob (`hasjob`) | Wuzzuf probe closed/expired-heavy — skipped |
| Balkans RS / HR / BG | HelloWorld.rs (`helloworld_rs`) + Posao.hr (`posao_hr`) + Dev Global Jobs (`devglobaljobs`, BG default) | Startit feed empty; BG via aggregator not Jobs.bg scrape |
| Africa KE | Jobweb Kenya (`jobweb_kenya`) | First Africa ACTIVE; NG/ZA/EG still gaps |
| PT / EU tech | Landing.jobs (`landing_jobs`) + okemprego (`okemprego`, PT `it-data`) | Iberia IT dual path; BR/AO via `OKEMPREGO_COUNTRIES` if needed |
| UA IT | DOU.ua (`dou_ua`) category RSS | Strong Java/Python category feeds |
| Design/dev remote | Authentic Jobs (`authentic_jobs`) FeedBurner RSS | Site `/rss` is editorial — use FeedBurner |

ATS boards (Greenhouse/Lever/Ashby/SmartRecruiters) follow **configured company lists**, not countries.

## Professional (IT persona)

| Role cluster | Coverage note |
|--------------|---------------|
| Java / Spring / Backend | Present in Remotive/Muse/ATS when employers post; query filters help |
| AI / LLM / RAG | Rising on remote boards; not saturated measurement |
| Freelance B2B marketplaces | Malt/Upwork/etc. **NEEDS_CREDENTIALS** — major gap vs contractor reality |
| Day rates | Sparse; NULL when undeclared — never invented |

## Source-type gaps

1. **Marketplace freelance APIs** — blocked on credentials/partnerships.
2. **National PES APIs** — registration required (FR, DE, US, …).
3. **Salary surveys** — report/import path only; not live connectors.
4. **Procurement (TED, SAM, …)** — different entity from jobs; Later module.
5. **Statistics (Eurostat, BLS, …)** — open data ingest Later; do not mix series.

## Next integrations (when credentials available)

Priority order for NEEDS_CREDENTIALS:

1. Adzuna / USAJOBS / France Travail / Bundesagentur — scaffolds ready; live keys → ACTIVE
2. Authorized marketplace exports (Malt/Upwork) if permitted

## How to expand

1. Update `data/sources/catalog.json` via `backend/scripts/generate_source_catalog.py` (or edit JSON).
2. Implement collector under `backend/app/collectors/`.
3. Register in `COLLECTORS`.
4. Live test → set status `ACTIVE` only after real records.
5. `POST /api/v1/admin/seed` to sync DB.
