# Next connector shortlist (from candidate analysis)

Derived from [`candidates/INDEX.md`](candidates/INDEX.md) + ADR-003.  
Already-ACTIVE: [`../INDEX.md`](../INDEX.md) (43+ DONE free, 8 scaffolds, FX/manual helpers).

## P0 — shipped / next

| ID | Source | Status | Sheet | Env |
|----|--------|--------|-------|-----|
| 93 | **Teamtailor** | **ACTIVE** (`teamtailor`) | [teamtailor.md](teamtailor.md) | `TEAMTAILOR_HOSTS` |
| 94 | **Recruitee** | **ACTIVE** (`recruitee`) | [recruitee.md](recruitee.md) | `RECRUITEE_SLUGS` |
| 96 | **Pinpoint** | **ACTIVE** (`pinpoint`) | [pinpoint.md](pinpoint.md) | `PINPOINT_SUBDOMAINS` |
| 87 | **Workable** | **ACTIVE** (`workable`) | [workable.md](workable.md) | `WORKABLE_SLUGS` |
| 88 | **Workday** | **ACTIVE** (`workday`) | [workday.md](workday.md) | `WORKDAY_TENANTS` |
| 95 | **BambooHR** | collector wired; default `flyio`; catalog **UNDER_REVIEW** (DC may 503) | [bamboohr.md](bamboohr.md) | `BAMBOOHR_COMPANIES` |
| 21 | Technojobs | **DEFERRED** — RSS lander wall (2026-10-21) | [21-technojobs.md](candidates/21-technojobs.md) | — |
| 8 | **Find a Job UK DWP** | scaffold **NEEDS_CREDENTIALS** (`findajob_dwp`) | [findajob_dwp.md](findajob_dwp.md) | `FINDAJOB_DWP_API_ID` / `FINDAJOB_DWP_API_KEY` |
| 45 | **Freelancer.com** | scaffold **NEEDS_CREDENTIALS** (`freelancer`) | [freelancer.md](freelancer.md) | `FREELANCER_OAUTH_TOKEN` |

Candidate research retained: [93-teamtailor.md](candidates/93-teamtailor.md), [94-recruitee.md](candidates/94-recruitee.md), [96-pinpoint.md](candidates/96-pinpoint.md).

## P1 — credentialed / partner (not free)

| ID | Source | Status | Note |
|----|--------|--------|------|
| 33 | VDAB | **PARTNER_ONLY** | Vacature v4 needs `X-IBM-Client-Id` + often partnership; CoE may freeze new apps — [33-vdab.md](candidates/33-vdab.md) |
| — | Existing scaffolds | keys empty | Adzuna, USAJOBS, France Travail, BA, Jooble, Findwork, Careerjet, InfoJobs |
| 8 | Find a Job UK DWP | scaffolded | Set gov keys → live probe → promote |

**Skip:** catalog 41 NAV Stillingsfeed = ACTIVE `nav_stilling_feed` (dump); search twin `nav_arbeidsplassen` (catalog 180).

## Do not scrape

| Analysis | Examples |
|----------|----------|
| `BLOCKED_TOS` | Indeed, LinkedIn, Glassdoor Jobs, SimplyHired, FlexJobs |
| `PARTNER_ONLY` | Malt, most UK commercial boards, agency brands, VDAB (until agreement) |

## Suggested build order

1. ~~Teamtailor + Recruitee + Pinpoint + Workable + Workday~~ **done** (2026-10-21)  
2. Expand ATS allowlists (GH 35 / Ashby 18 / Workday 15 / Workable +`riot`) as boards are probed  
3. BambooHR: default `flyio` set; re-probe on DC (may 503) → expand `BAMBOOHR_COMPANIES` → promote ACTIVE after inserts  
4. Operator keys/tokens for scaffolds (Adzuna, USAJOBS, DWP, Freelancer, Findwork, …) — needs secrets in `.env`  
5. ~~Technojobs~~ deferred (RSS → `/lander` HTML; not ADR-003-safe)  
6. Recruitee: add `X-Careers-Sites-Token` before **2027-02-10**  
7. VDAB only after open-data app + partnership clarity  

## Coverage snapshot

| Bucket | Count |
|--------|------:|
| Connector analysis sheets | 59 |
| Candidate sheets | 139 |
| Job-ish A–D `TODO_ACCESS` | **0** |
| Remaining `TODO_ACCESS` | 12 (G/H/I reference / procurement only) |
