# Wellfound (catalog_id=65)

| Field | Value |
|-------|-------|
| Analysis | BLOCKED_TOS |
| Category | B |
| verification_status | UNDER_REVIEW |
| access_mode | unknown |
| connector_key | — |

## Official / docs
- Official: https://wellfound.com/ (formerly AngelList Talent).
- Docs / developer: No public job-search API or developer program for bulk listings. Legacy `api.angel.co` REST is defunct. In-app `/graphql` is session/CSRF-bound, not a documented open endpoint.
- Terms / robots notes: Bot protection (e.g. DataDome) on job routes; full filters/salary often login-gated. Recruiter **MCP** at `https://wellfound.com/api/mcp` (OAuth, `applications:read`) serves hiring workflows, not an open job corpus ([Help: Connect Wellfound to AI](https://help.wellfound.com/article/1219-connect-wellfound-to-your-ai-assistant)).

## Access path (for future connector)
- Preferred: licensed data export or explicit partnership — not self-serve job dump.
- Endpoint candidates (method + URL): none suitable for Demand Compass ingest without recruiter/enterprise agreement.
- Auth: Recruiter OAuth for MCP only; not a substitute for public job RSS/API.
- Pagination: N/A for authorized research path.

## Job list / page structure (if known)
- Content-Type: Next.js app; listing data embedded in page bootstrap JSON when authenticated — not authorized for automated harvest.
- Public startup job UX overlaps free boards already in catalog (Jobicy, Himalayas, HN hiring).

## Field map sketch → RawJob
| Source | RawJob | Notes |
|--------|--------|-------|
| — | — | No authorized mapping |

## Geo / role fit
- Countries: startup/tech US + global remote.
- Fit for FMI Demand Compass: **Low** without partnership; prefer documented startup feeds elsewhere.

## Gaps / next step
- Ask Wellfound for research/data partnership if needed; do not scrape or call undocumented GraphQL ([ADR-003](../../decisions/ADR-003-authorized-connectors-only.md)).
- Treat recruiter MCP as PARTNER_ONLY hiring tool, out of scope for open job corpus.
