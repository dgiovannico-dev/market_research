# Plan: Global sources expansion

## Goal

Complete and extend the global data-sources program: honest catalog, working connectors for every technically authorized source, credential backlog, stats/procurement Later paths—without inventing access or test results.

Product alignment: [PRODUCT.md](../../PRODUCT.md) · [SPEC-sources.md](../../specs/SPEC-sources.md) · [ADR-005](../../decisions/ADR-005-global-source-catalog.md).

## Deliverable checklist (prompt §7)

| # | Deliverable | Status |
|---|-------------|--------|
| 1 | Full source registry with verification status | Done — `data/sources/catalog.json` |
| 2 | Official URLs / docs consulted | Done — catalog fields + validation report |
| 3 | Validation report per source (summary + evidence) | Done — [VALIDATION_REPORT.md](../../sources/VALIDATION_REPORT.md) |
| 4 | Working connectors for accessible sources | Done for public ACTIVE set; expand with keys |
| 5 | Services needing credentials / agreements | Done — `NEEDS_CREDENTIALS` in catalog |
| 6 | Non-integrable sources + reasons | Done — `REJECTED` / gaps doc |
| 7 | DB + migrations | Done — catalog fields + verifications |
| 8 | Collection / update pipeline | Done — collectors + scheduler hook |
| 9 | Dedup + normalization | Done baseline; deepen as sources grow |
| 10 | Sources management dashboard | Done — `/sources` + catalog APIs |
| 11 | Analytics dashboard | Done baseline; combo demand filters Next |
| 12 | Automated tests + real results | Done pytest/live collectors; re-run on new connectors |
| 13 | Install / config instructions | Done — root README + `.env.example` |
| 14 | `.env.example`, Compose, README | Done |
| 15 | Geographic / professional coverage gaps | Done — [COVERAGE_GAPS.md](../../sources/COVERAGE_GAPS.md) |

## Next implementation slices

### Slice A — Credentialed job APIs (when keys exist)

Order: Adzuna → USAJOBS → Reed → France Travail / Bundesagentur → others with official APIs.

Per connector:

1. Store secrets only via env / secret manager (never in catalog JSON).
2. Implement collector + register in `COLLECTORS`.
3. Live test with real data → set catalog `ACTIVE`.
4. Pytest + smoke; update VALIDATION_REPORT and COVERAGE_GAPS.

### Slice B — ATS board registry growth

Grow Greenhouse/Lever/Ashby tenant lists from a maintained allowlist; never assume cross-tenant search.

- [x] 2026-10-20 expand: Greenhouse +5 (`gusto`,`pinterest`,`reddit`,`coursera`,`khanacademy`), Ashby +2 (`granola`,`runway`); prune 404s from probe defaults; catalog/VALIDATION notes synced. Further growth still open as boards are re-probed.

### Slice C — Taxonomy / FX

Keep Frankfurter/ECB; optional Open Exchange Rates when key; ESCO/O*NET sync as dedicated Later tasks.

### Slice C2 — Nordic PES (shipped starter)

- [x] Arbetsförmedlingen JobTech JobSearch (`arbetsformedlingen`) ACTIVE — public, no key

### Slice D — Stats-ingest (Later)

Open data downloaders with series metadata (unit, periodicity, methodology). No cross-country sums without comparability check.

### Slice E — Procurement (Later)

TED / Contracts Finder / SAM as **tenders**, not jobs. Separate tables and UI.

## Acceptance for any new ACTIVE source

- [ ] Official access path documented in catalog
- [ ] Connector returns real records in CI or documented live probe
- [ ] Dedup keys mapped
- [ ] Status flipped only after evidence
- [ ] Coverage gaps updated

## Risks

| Risk | Mitigation |
|------|------------|
| False ACTIVE claims | ADR-003/005; tests gate status |
| ToS scrape temptation | Reject; manual import / partner only |
| Stats vs jobs confusion | Separate modules Later |
| Remote-board bias | Document gaps; prioritize PES/Adzuna with keys |

## References

- Catalog: [`data/sources/catalog.json`](../../../data/sources/catalog.json)
- Tasks: [../../../tasks/todo.md](../../../tasks/todo.md) (Tasks 10+)
