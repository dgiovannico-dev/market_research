#!/usr/bin/env node
/**
 * Capture Atlas UI screenshots for docs after market data has painted.
 * Usage: node scripts/capture_docs_screenshots.mjs
 */
import { chromium } from "playwright";
import { mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const DST = join(ROOT, "docs/assets/screenshots");
const BASE = process.env.FRONTEND_URL || "http://127.0.0.1:3000";

/** Demo local profile so Stack Compass / Study Advisor render recommendations. */
const DEMO_PROFILE = {
  display_name: "Docs capture",
  residence_country: "IT",
  target_rate_amount: "550",
  rate_currency: "EUR",
  rate_unit: "day",
  skills: ["Python", "TypeScript", "Kubernetes", "PostgreSQL", "React"],
  certifications: ["AWS Solutions Architect", "CKA"],
};

const PAGES = [
  { file: "01-executive.png", path: "/en" },
  { file: "02-market-scan.png", path: "/en/market-scan" },
  { file: "03-trends.png", path: "/en/trends" },
  { file: "04-stack.png", path: "/en/stack", seedProfile: true },
  { file: "05-certifications.png", path: "/en/certifications" },
  { file: "06-focus.png", path: "/en/focus" },
  { file: "07-assistant.png", path: "/en/assistant" },
  { file: "08-profile.png", path: "/en/profile", seedProfile: true, analyzeGaps: true },
  { file: "09-learn.png", path: "/en/learn", seedProfile: true, generatePlan: true },
  { file: "10-jobs.png", path: "/en/jobs" },
  { file: "11-sources.png", path: "/en/sources" },
  { file: "12-quality.png", path: "/en/quality" },
];

const LOADING_RE =
  /Summary still loading|still loading|Loading…|Loading\.\.\.|Caricamento/i;

async function waitForData(page, { timeout = 90000 } = {}) {
  await page.waitForLoadState("domcontentloaded");
  // Give React a beat to mount fetchers
  await page.waitForTimeout(800);

  const deadline = Date.now() + timeout;
  while (Date.now() < deadline) {
    const busy = await page.evaluate((reSrc) => {
      const re = new RegExp(reSrc, "i");
      const text = document.body?.innerText || "";
      if (re.test(text)) return true;
      // aria-busy / skeleton markers
      if (document.querySelector('[aria-busy="true"]')) return true;
      if (document.querySelector('[data-loading="true"]')) return true;
      return false;
    }, LOADING_RE.source);

    if (!busy) {
      // settle charts / layout
      await page.waitForTimeout(1500);
      const still = await page.evaluate(
        (reSrc) => new RegExp(reSrc, "i").test(document.body?.innerText || ""),
        LOADING_RE.source,
      );
      if (!still) return;
    }
    await page.waitForTimeout(500);
  }
  throw new Error(`Timed out waiting for data on ${page.url()}`);
}

async function seedProfile(page) {
  await page.addInitScript((profile) => {
    localStorage.setItem("fmi:userProfile:v1", JSON.stringify(profile));
  }, DEMO_PROFILE);
}

async function maybeGeneratePlan(page) {
  const btn = page.getByRole("button", { name: /Generate plan/i });
  if ((await btn.count()) === 0) return;
  if (await btn.isDisabled()) return;
  await btn.click();
  // Wait until generation finishes and week calendar / plan card appear
  await page
    .getByRole("button", { name: /^Generate plan$/i })
    .waitFor({ state: "visible", timeout: 120000 })
    .catch(() => {});
  await page
    .getByRole("heading", { name: /Week calendar/i })
    .waitFor({ state: "visible", timeout: 120000 })
    .catch(() => {});
  await page
    .getByText(/Your study plan|Focus on /i)
    .first()
    .waitFor({ state: "visible", timeout: 60000 })
    .catch(() => {});
  await waitForData(page);
  await page.waitForTimeout(1500);
}

async function maybeAnalyzeGaps(page) {
  const btn = page.getByRole("button", { name: /Save & analyze gaps/i });
  if ((await btn.count()) === 0) return;
  await btn.click();
  await page.waitForTimeout(2500);
  await waitForData(page);
  // Prefer a frame that shows gap rows when available
  await page
    .getByText(/Priority skill gaps/i)
    .waitFor({ state: "visible", timeout: 10000 })
    .catch(() => {});
  await page.waitForTimeout(1500);
}

async function main() {
  mkdirSync(DST, { recursive: true });
  const browser = await chromium.launch({ headless: true });

  for (const spec of PAGES) {
    const { file, path } = spec;
    const url = `${BASE}${path}`;
    process.stdout.write(`Capturing ${file} ← ${url} … `);

    const context = await browser.newContext({
      viewport: { width: 1440, height: 900 },
      deviceScaleFactor: 1,
    });
    const page = await context.newPage();
    if (spec.seedProfile) await seedProfile(page);

    await page.goto(url, { waitUntil: "networkidle", timeout: 120000 });
    await waitForData(page);
    if (spec.analyzeGaps) await maybeAnalyzeGaps(page);
    if (spec.generatePlan) await maybeGeneratePlan(page);

    // Stack / learn: wait until empty-profile stub is gone when seeded
    if (spec.seedProfile) {
      await page
        .getByText(/Add at least 3 skills/i)
        .waitFor({ state: "hidden", timeout: 15000 })
        .catch(() => {});
      await page.waitForTimeout(2000);
    }

    // Ensure site credit footer is painted (full-page shot includes it)
    await page
      .getByRole("contentinfo")
      .waitFor({ state: "visible", timeout: 15000 })
      .catch(() => {});
    await page.waitForTimeout(400);

    const out = join(DST, file);
    // Playwright clip cannot exceed the viewport — grow viewport (capped)
    // so docs embeds stay readable; in-app lists use Expand all.
    const MAX_SHOT_H = Number(process.env.DOCS_SHOT_MAX_H || 2800);
    const contentH = await page.evaluate(() =>
      Math.max(
        document.documentElement.scrollHeight,
        document.body?.scrollHeight || 0,
      ),
    );
    const shotH = Math.min(Math.max(contentH, 900), MAX_SHOT_H);
    await page.setViewportSize({ width: 1440, height: shotH });
    await page.evaluate(() => window.scrollTo(0, 0));
    await page.waitForTimeout(200);
    await page.screenshot({ path: out });
    await context.close();
    console.log("ok");
  }

  await browser.close();
  console.log(`Done → ${DST}`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
