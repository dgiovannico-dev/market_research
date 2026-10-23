# Idea: Query-first research corpus (superseded)

**Status:** superseded 2026-10-20  
**Successor:** [freelance-demand-compass.md](./freelance-demand-compass.md)

## Why superseded

The first draft correctly banned silent env topic defaults (`*_DEFAULT_QUERY=java`) and promoted user `SearchQuery` intents. It incorrectly made **user intents the only** topic-scoped sync path, which creates **confirmation bias**: freelancers cannot discover rising/cooling demand outside keywords they already know.

Kept decisions that remain valid:

- No silent env topic defaults on the product path.
- User free text → Research Intents with `query_id` provenance.
- Explore is DB-first; live refresh is explicit.
- LLM/MCP read only observed DB evidence.

Evolved in the Demand Compass:

- Dual corpus: **discovery** (market scan) + **focus** (user bets).
- Analytics lenses: `market` | `focus` | `compare`.
- LLM as evidence coach (rising/cooling, geo, adjacent, watch suggestions with accept).
