# ADR-003: Authorized / public connectors only

## Status

Accepted

## Date

2026-10-20

## Context

Job boards often prohibit scraping. Legal and ethical risk outweighs coverage gains for a production-oriented product. A large global catalog (~193 candidates) creates pressure to “integrate everything”; only authorized automation paths may become `ACTIVE`.

## Decision

Only run connectors that are public APIs, public feeds, documented public ATS board endpoints, or explicitly authorized partner/credential paths. Sources needing credentials or partnerships remain in the catalog with `NEEDS_CREDENTIALS` / `requires_credentials` (or `unsupported` / `REJECTED`) and are **not runnable**. No CAPTCHA/paywall/auth bypass.

**Cost preference:** when a free public API/RSS/feed covers the same need as a paid aggregator API, implement and prefer the free path first (e.g. Jobicy / Himalayas / HN Algolia over paid Adzuna/Jooble/Indeed). Paid/credentialed scaffolds stay available for operators who have keys; they do not justify scraping the web site instead.

Verification statuses (catalog): `DISCOVERED` · `UNDER_REVIEW` · `NEEDS_CREDENTIALS` · `PENDING_ACCESS` · `VALIDATED` · `IMPLEMENTED` · `ACTIVE` · `DEGRADED` · `BLOCKED` · `DEPRECATED` · `REJECTED`.

`ACTIVE` requires real records from a connector in this repo under test. Manual import remains a first-class path for licensed dumps and non-automatable reports.

## Alternatives considered

### Aggressive scraping

- Pros: more rows
- Cons: ToS/legal risk, brittle, unethical for this product positioning
- Rejected

### Hide unsupported sources

- Pros: cleaner UI
- Cons: less honest about coverage
- Rejected; status stays visible on Sources + catalog API

### Invent credentials success in docs

- Pros: looks complete
- Cons: false claims
- Rejected; evidence in [../sources/VALIDATION_REPORT.md](../sources/VALIDATION_REPORT.md)

## Consequences

- Coverage notes on Sources page and [../sources/COVERAGE_GAPS.md](../sources/COVERAGE_GAPS.md).
- LinkedIn/Malt/Indeed/Upwork/Adzuna/etc. stay Next/Later until authorized.
- Ingest and sources specs must stay aligned with this ADR.
- Discovery indexes (Public APIs lists) are not proof a service is usable.
- **Spain ES:** prefer Tecnoempleo documented RSS syndication (`alertas-empleo-rss.php`); do **not** scrape Empléate/SEPE Solr vacancy search.
