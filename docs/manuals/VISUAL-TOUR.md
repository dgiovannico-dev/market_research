# Visual tour (video + screenshots)

**Who should read this:** Anyone who wants to *see* how FMI works before reading the manuals.

**What you will learn:** A recommended path through Atlas. Prefer the **videos** (human pace, on-screen captions). Still frames below remain for Markdown preview and print.

Start the app with [ops/LOCAL.md](../ops/LOCAL.md), then open `http://localhost:3000/en` to click along live.

## Product videos (start here)

| Video | Duration | Covers |
|-------|----------|--------|
| [Full platform](../assets/videos/00-full-platform.mp4) | ~10+ min | Every Atlas zone; each page scrolled top→bottom |
| [Explore](../assets/videos/01-explore.mp4) | ~5 min | Executive → Stack; full-page scroll on every screen |
| [Jobs & career](../assets/videos/02-jobs-career.mp4) | ~2.5 min | Job Explorer, profile + gaps, Study Advisor, applications |
| [Ops](../assets/videos/03-ops.mp4) | ~3 min | Data quality, sources catalog, alerts (no credentialed runs) |
| [Research](../assets/videos/04-research.mp4) | ~1.5 min | Focus intents, report, assistant |

<video controls width="100%" src="../assets/videos/00-full-platform.mp4">
  <a href="../assets/videos/00-full-platform.mp4">Download full platform tour (MP4)</a>
</video>

Index and re-record notes: [../assets/videos/README.md](../assets/videos/README.md).

```mermaid
flowchart LR
  V0[Full platform video] --> E[Explore]
  V0 --> J[Jobs]
  V0 --> O[Ops]
  V0 --> R[Research]
  E --> E1[Executive / Trends / Stack]
  J --> J1[Jobs / Profile / Learn]
  O --> O1[Quality / Sources]
  R --> R1[Focus / Assistant]
```

---

## Still frames (optional)

Same order as a short product scrub—use when you cannot play video.

### 1. Executive — “What is moving?”

Landing desk: rising/cooling, geo, mixes. Always read **n=** and coverage notes in Guided mode.

![Executive](../assets/screenshots/01-executive.png)

→ Details: [EXPLORE.md](EXPLORE.md#executive--)

### 2. Market scan — discovery probes

Enable broad discovery topics that feed the **Market** lens. These are not your personal focus bets.

![Market scan](../assets/screenshots/02-market-scan.png)

### 3. Trends — skills rising vs cooling

Half-period growth on observed skill mentions. Status `insufficient_data` means do not trust the %.

![Trends](../assets/screenshots/03-trends.png)

### 4. Stack Compass — what to learn next

Compares your local profile skills to market co-occurrence / gaps.

![Stack Compass](../assets/screenshots/04-stack.png)

### 5. Certifications — market cert signals

Observed cert mentions (taxonomy-backed), including by-country views.

![Certifications](../assets/screenshots/05-certifications.png)

### 6. My focus — personal research intents

Create **focus** intents; Sync pulls matching jobs into the Focus lens.

![Focus](../assets/screenshots/06-focus.png)

→ [RESEARCH.md](RESEARCH.md)

### 7. Assistant — evidence briefs

Ask for rising/cooling, geo, adjacent skills, or suggest watches—**Accept** before a watch is persisted.

![Assistant](../assets/screenshots/07-assistant.png)

### 8. Profile — skills you claim

Stored in **browser localStorage** (not multi-device sync). Feeds Stack and Learn.

![Profile](../assets/screenshots/08-profile.png)

→ [CAREER.md](CAREER.md)

### 9. Learn — Study Advisor

Turns Stack evidence into a structured study plan (optional LLM refine when configured).

![Learn](../assets/screenshots/09-learn.png)

### 10. Jobs — inventory

Canonical job list with filters; still observed DB rows, not “all jobs on the internet.”

![Jobs](../assets/screenshots/10-jobs.png)

### 11. Sources — operators

Run ACTIVE connectors, browse catalog, manage credentials / LLM (admin).

![Sources](../assets/screenshots/11-sources.png)

→ [ADMIN.md](ADMIN.md) · deep ops [../ops/RUNBOOKS.md](../ops/RUNBOOKS.md)

### 12. Quality — corpus health

Read-only view of missingness / source health before you trust a KPI.

![Quality](../assets/screenshots/12-quality.png)

---

## Next

- Shared concepts (lens, evidence, auth): [OVERVIEW.md](OVERVIEW.md)
- Architecture diagrams: [../architecture/OVERVIEW.md](../architecture/OVERVIEW.md)
- Asset index: [../assets/README.md](../assets/README.md)
