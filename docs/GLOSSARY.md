# Glossary

Ubiquitous language for product, ADRs, and code. One meaning per term in this system.

| Term | Meaning | See |
|------|---------|-----|
| **Observed ≠ market size** | KPIs mean records in *this* database, never invented totals | [ADR-001](decisions/ADR-001-evidence-first-kpis.md) |
| **Evidence kind** | How a fact was obtained: `observed`, `extracted`, `inferred`, `derived`, `estimated`, `manually_verified` | ADR-001, ADR-002 |
| **Evidence tier** | Corpus quality: `standard` (usable body) vs `thin` (title/snippet/capped). Analytics default `min_evidence=standard` | ADR-001 |
| **KPI / sample size / coverage_notes** | Methodology travels with the number; growth may be `insufficient_data` | ADR-001 |
| **Catalog** | System of record for source candidates (`data/sources/catalog.json`); size ≠ coverage | [ADR-005](decisions/ADR-005-global-source-catalog.md) |
| **Connector** | Runnable ingest path; strict subset of catalog entries | [ADR-003](decisions/ADR-003-authorized-connectors-only.md) |
| **Verification status** | Catalog lifecycle through `ACTIVE`. `ACTIVE` only after real connector evidence | ADR-003, ADR-005 |
| **Collection mode** | `search` (needs query) \| `dump` \| `feed` (no topic string) | [ADR-007](decisions/ADR-007-query-first-sync.md) |
| **Research intent (`SearchQuery`)** | User/seed probe; `kind`: **discovery** \| **focus** | ADR-007 |
| **`job_intent_matches`** | Normative provenance Job ↔ intent (not sole `jobs.query_id`) | ADR-007 |
| **Lens** | Corpus filter for analytics/UI/MCP: `market` \| `focus` \| `compare` | ADR-007 |
| **Demand Compass** | Rising/cooling, geo, evidence coach — not a market oracle | ADR-007 |
| **Classification mode** | `rules` \| `hybrid` \| `llm` | [ADR-002](decisions/ADR-002-classification-modes.md) |
| **View mode** | Presentation only: `guided` \| `trends_only` — APIs stay evidence-first | [ADR-004](decisions/ADR-004-dashboard-modes.md) |
| **DashboardSpec / ReportSpec** | Validated LLM/MCP outputs; not free-form SQL to UI | [ADR-006](decisions/ADR-006-mcp-schema-driven-analytics.md) |
| **CLOSED_JOB_STATUSES** | `closed`, `closed_stale`, `removed_from_source` — excluded from DSS corpus | `app.storage.enums` |
| **RawJob** | Anti-corruption DTO from collectors into ingestion | `collectors/` |
| **Collection run / daily crawler** | Budgeted sync: dump → discovery → focus; no silent env topic defaults | ADR-007 |

**Read next**

- Pictures first: [manuals/VISUAL-TOUR.md](manuals/VISUAL-TOUR.md)
- Architecture diagrams: [architecture/OVERVIEW.md](architecture/OVERVIEW.md)
- Database / ER: [architecture/DATABASE.md](architecture/DATABASE.md)
- Connector alignment: [ops/RUNBOOKS.md](ops/RUNBOOKS.md)
- Screenshot gallery: [assets/README.md](assets/README.md)
