# Product tour videos

Screen recordings of the live Atlas UI at a **human-followable** pace (captions on screen, ~1–3s pauses after clicks, **scroll through each page to the bottom**). Prefer these over still screenshots when teaching someone how FMI works.

| File | Zone | What it shows |
|------|------|----------------|
| [00-full-platform.mp4](00-full-platform.mp4) | All | Continuous walkthrough of every Atlas zone |
| [01-explore.mp4](01-explore.mp4) | Explore | Executive, market scan, explorer, trends, skills, relations, rates, geo, languages, certs, Stack Compass |
| [02-jobs-career.mp4](02-jobs-career.mp4) | Jobs | Job Explorer filters, local profile + gap analysis, Study Advisor (busy hours, week calendar, plan card), applications |
| [03-ops.mp4](03-ops.mp4) | Ops | Data quality KPIs, sources catalog / LLM panel (no credentialed runs), alerts |
| [04-research.mp4](04-research.mp4) | Research | Focus intents, period report, assistant briefs |

Open the `.mp4` in any player, or from [VISUAL-TOUR.md](../../manuals/VISUAL-TOUR.md).

## Re-record

Stack must be up with ingested market data:

```bash
# all zone videos + full platform (long)
node scripts/record_docs_videos.mjs

# one zone
node scripts/record_docs_videos.mjs explore
```

Needs Playwright Chromium and `ffmpeg` on PATH. Demo profile skills are seeded so Stack / Learn show recommendations.
