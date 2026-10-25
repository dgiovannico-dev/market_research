# Visual assets

**Videos first** — human-paced screen recordings of the live Atlas UI. Screenshots remain for Markdown embeds and print.

Architecture and ops docs also use **Mermaid** diagrams (flowchart, sequence, ER).

## Product videos

See [videos/README.md](videos/README.md).

| File | Zone |
|------|------|
| [videos/00-full-platform.mp4](videos/00-full-platform.mp4) | Full walkthrough |
| [videos/01-explore.mp4](videos/01-explore.mp4) | Explore |
| [videos/02-jobs-career.mp4](videos/02-jobs-career.mp4) | Jobs & career |
| [videos/03-ops.mp4](videos/03-ops.mp4) | Ops |
| [videos/04-research.mp4](videos/04-research.mp4) | Research |

Linked from [manuals/VISUAL-TOUR.md](../manuals/VISUAL-TOUR.md).

### Re-record videos

```bash
node scripts/record_docs_videos.mjs           # all zones + full
node scripts/record_docs_videos.mjs explore   # one zone
```

Needs Playwright Chromium, `ffmpeg`, and a running stack with market data.

## Screenshot gallery

| File | Screen | Used in |
|------|--------|---------|
| [screenshots/01-executive.png](screenshots/01-executive.png) | Executive home | [manuals/OVERVIEW](../manuals/OVERVIEW.md), [EXPLORE](../manuals/EXPLORE.md) |
| [screenshots/02-market-scan.png](screenshots/02-market-scan.png) | Market scan | EXPLORE, VISUAL-TOUR |
| [screenshots/03-trends.png](screenshots/03-trends.png) | Technology trends | EXPLORE |
| [screenshots/04-stack.png](screenshots/04-stack.png) | Stack Compass | EXPLORE |
| [screenshots/05-certifications.png](screenshots/05-certifications.png) | Certifications | EXPLORE |
| [screenshots/06-focus.png](screenshots/06-focus.png) | My focus | [RESEARCH](../manuals/RESEARCH.md) |
| [screenshots/07-assistant.png](screenshots/07-assistant.png) | Assistant briefs | RESEARCH |
| [screenshots/08-profile.png](screenshots/08-profile.png) | Local profile | [CAREER](../manuals/CAREER.md) |
| [screenshots/09-learn.png](screenshots/09-learn.png) | Study Advisor | CAREER |
| [screenshots/10-jobs.png](screenshots/10-jobs.png) | Jobs list | CAREER |
| [screenshots/11-sources.png](screenshots/11-sources.png) | Sources / ops hub | [ADMIN](../manuals/ADMIN.md) |
| [screenshots/12-quality.png](screenshots/12-quality.png) | Data quality | ADMIN |

### Refresh screenshots

```bash
node scripts/capture_docs_screenshots.mjs
```

Waits for “Summary still loading…” to clear; seeds a demo profile for Stack/Learn. Do **not** use instant Chrome `--screenshot`.
