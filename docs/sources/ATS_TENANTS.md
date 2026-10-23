# ATS tenant allowlist

Greenhouse, Lever, Ashby, SmartRecruiters, Personio, Teamtailor, Recruitee, Pinpoint, Workable, Workday, and BambooHR collectors only call **public** board/posting endpoints for tenants listed in env. There is no cross-tenant search.

Collectors cap **40 jobs per tenant** so expanding the allowlist stays safe for ingest.

## Env vars

| Variable | Example | Notes |
|----------|---------|-------|
| `GREENHOUSE_BOARDS` | `airbnb,stripe,gitlab,…,khanacademy,lyft` | Board tokens from `boards.greenhouse.io/<token>` |
| `LEVER_SITES` | `spotify,palantir,wealthfront` | Site slugs from `jobs.lever.co/<site>` (probe before adding; slugs churn) |
| `ASHBY_ORGS` | `notion,linear,vercel,openai,ramp,cursor,warp,granola,runway,supabase` | Org slugs for Ashby public job board API; empty → non-runnable |
| `SMARTRECRUITERS_COMPANIES` | `endava,ServiceNow,DeliveryHero,Wise,Allegro,Uber` | Company identifiers for `api.smartrecruiters.com/v1/companies/{id}/postings` |
| `PERSONIO_COMPANIES` | `1komma5grad,chrono24,…,researchgate` | Company slugs from `{slug}.jobs.personio.de` → `GET …/search.json` (public listing JSON) |
| `TEAMTAILOR_HOSTS` | `polestar.teamtailor.com,careers.oatly.com,…` | Career host or custom domain → `GET https://{host}/jobs.json` |
| `RECRUITEE_SLUGS` | `jobs,personio,bunq,adjust` | Slugs for `GET https://{slug}.recruitee.com/api/offers/` (keyless until **2027-02-10**) |
| `PINPOINT_SUBDOMAINS` | `made-tech,accenture,…` | Subdomains for `GET https://{sub}.pinpointhq.com/postings.json` (skip demo-like boards) |
| `WORKABLE_SLUGS` | `huggingface,jasper,skillshare,riot` | Slugs for `GET apply.workable.com/api/v1/widget/accounts/{slug}` (many brand guesses return `jobs:[]`; back off on **429**) |
| `WORKDAY_TENANTS` | `nvidia:wd5:NVIDIAExternalCareerSite,…` | `tenant:wdN:siteSlug` for `POST …/wday/cxs/{tenant}/{site}/jobs` (wrong shard/site → **422**) |
| `BAMBOOHR_COMPANIES` | `flyio` | Subdomains for `GET https://{slug}.bamboohr.com/careers/list` — do **not** follow redirects to marketing; many DC IPs still get **503** — only add slugs that return **200 + non-empty** `result` from *your* egress |

Comma-separated, no secrets. Restart API / re-seed after changes so `Source` rows stay aligned.

## How to add a tenant

1. Confirm the company exposes a **public** careers board (no login).
2. Probe with `./backend/scripts/probe_ats_tenants.sh` (or curl the public API).
3. Add the slug/token to the matching env var in `.env` (and optionally `.env.example` defaults).
4. Run seed (or restart with seed-on-start) and `POST /api/v1/sources/{id}/run`.
5. Only mark catalog evidence ACTIVE when a live run returns jobs.

## IT / CH / LU focus (2026-10-22)

Probed green and added to defaults (see [IT_CH_LU_COVERAGE.md](IT_CH_LU_COVERAGE.md)):

| Geo | Tenant | Collector |
|-----|--------|-----------|
| IT | `satispay`, `docebo` | Ashby |
| IT | `thefork`, `truelayer` | Greenhouse |
| IT | `musixmatch` | Lever |
| IT | `moneyfarm` | Workable |
| IT | `bendingspoons` | Pinpoint (already listed) |
| LU | `Talan`, `Devoteam` | SmartRecruiters |
| CH | `swisscom:wd103:SwisscomExternalCareers` | Workday |
| CH/LU | `juliusbaer:wd3:External` | Workday (Zurich + Luxembourg offices) |

Probed 2026-10-23 green (non-empty): `docebo` Ashby ~45, `thefork` GH ~29 (Milan/Turin), `truelayer` GH (Milan), `juliusbaer` Workday ~179. Scalapay Greenhouse slug no longer 200 — do not re-add without re-probe. Expand further with `./backend/scripts/probe_ats_tenants.sh` before adding slugs.

## Defaults in `.env.example`

Curated public boards last HTTP-probed green with non-empty payloads (2026-10-21, multi-agent wave + 2026-10-22 IT/CH/LU): Greenhouse (**69**), Lever (4, +`musixmatch`), Ashby (**52**, +`satispay`), Personio (**15**), Teamtailor (**26** Nordic/EU hosts), Recruitee (**9**), Pinpoint (**10**, +`hazelcast`,`smartthings`; still skip DEI demos), Workable (5, +`moneyfarm`), Workday (**38** CXS incl. Swisscom — retail megaboards CVS/Lowes/Target omitted), SmartRecruiters (+`Talan`,`Devoteam` for LU), BambooHR (`flyio` — 200+jobs; brand guesses often 302→marketing or empty `result`; DC may still 503). Join.com 410/401 — unused. Discover Workday site slugs from careers HTML, not blind `:External`. Teamtailor often uses custom domains + JSON Feed `items`. Re-probe before expanding. Do not scrape HTML careers pages.

```bash
# batch probe (override with … / PINPOINT_PROBE / WORKABLE_PROBE / WORKDAY_PROBE / BAMBOOHR_PROBE)
./backend/scripts/probe_ats_tenants.sh

# BambooHR only — no redirect follow; require HTTP 200 + non-empty result[] before adding
BAMBOOHR_PROBE="flyio cultureamp" ./backend/scripts/probe_ats_tenants.sh | grep '^bb:'
# or one-off:
curl -sS -o /tmp/bb.json -w "%{http_code}\n" -A "FMI-MarketIntel/1.0" -H "Accept: application/json" \
  "https://flyio.bamboohr.com/careers/list"   # expect 200; then: python3 -c "import json; print(len(json.load(open('/tmp/bb.json'))['result']))"
```

### BambooHR → ACTIVE

1. Probe from the same egress the API will use (compose/DC often **503**; home/residential may work).
2. Keep only slugs with **200** and **n > 0** jobs. Redirects (302→marketing) and empty `result` are not boards.
3. Set `BAMBOOHR_COMPANIES` in `.env`, restart API / re-seed.
4. `POST /api/v1/sources/{id}/run` for `bamboohr` — confirm inserts.
5. Flip catalog `verification_status` to ACTIVE and regenerate catalog (`scripts/generate_source_catalog.py` / project docs).
