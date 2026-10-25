#!/usr/bin/env node
/**
 * Record human-paced FMI docs videos (MP4) for all Atlas zones.
 *
 * Usage:
 *   node scripts/record_docs_videos.mjs              # all zone + full
 *   node scripts/record_docs_videos.mjs explore jobs  # subset
 *   TOURS=full node scripts/record_docs_videos.mjs
 *
 * Requires: playwright + chromium, ffmpeg, running frontend at FRONTEND_URL.
 */
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { recordTour } from "./docs_video/lib.mjs";
import {
  tourExplore,
  tourJobs,
  tourOps,
  tourResearch,
  tourFullPlatform,
} from "./docs_video/tours.mjs";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const OUT = join(ROOT, "docs/assets/videos");

const CATALOG = {
  explore: {
    fileBase: "01-explore",
    title: "Explore zone",
    run: tourExplore,
  },
  jobs: {
    fileBase: "02-jobs-career",
    title: "Jobs & career",
    run: tourJobs,
  },
  ops: {
    fileBase: "03-ops",
    title: "Ops",
    run: tourOps,
  },
  research: {
    fileBase: "04-research",
    title: "Research",
    run: tourResearch,
  },
  full: {
    fileBase: "00-full-platform",
    title: "Full platform",
    run: tourFullPlatform,
  },
};

async function main() {
  const argv = process.argv.slice(2).map((s) => s.toLowerCase());
  const envList = (process.env.TOURS || "")
    .split(/[,\s]+/)
    .map((s) => s.trim().toLowerCase())
    .filter(Boolean);
  let keys = argv.length ? argv : envList.length ? envList : Object.keys(CATALOG);

  // Prefer zone videos first, full last (full is long)
  const order = ["explore", "jobs", "ops", "research", "full"];
  keys = order.filter((k) => keys.includes(k));
  if (!keys.length) {
    console.error("Unknown tour keys. Use:", Object.keys(CATALOG).join(", "));
    process.exit(1);
  }

  console.log(`Recording → ${OUT}`);
  console.log(`Tours: ${keys.join(", ")}`);

  for (const key of keys) {
    const spec = CATALOG[key];
    process.stdout.write(`▶ ${spec.title} (${spec.fileBase}.mp4) … `);
    const t0 = Date.now();
    const path = await recordTour({
      outDir: OUT,
      fileBase: spec.fileBase,
      seed: true,
      run: spec.run,
    });
    const sec = ((Date.now() - t0) / 1000).toFixed(1);
    console.log(`ok (${sec}s) → ${path}`);
  }
  console.log("Done.");
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
