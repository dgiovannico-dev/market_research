/**
 * Shared helpers for human-paced FMI docs video tours (Playwright).
 */
import { chromium } from "playwright";
import { mkdirSync, renameSync, existsSync, readdirSync, unlinkSync } from "node:fs";
import { join } from "node:path";
import { spawnSync } from "node:child_process";

export const BASE = process.env.FRONTEND_URL || "http://127.0.0.1:3000";
export const LOCALE = "en";

export const DEMO_PROFILE = {
  display_name: "Demo user",
  residence_country: "IT",
  target_rate_amount: "550",
  rate_currency: "EUR",
  rate_unit: "day",
  skills: ["Python", "TypeScript", "Kubernetes", "PostgreSQL", "React"],
  certifications: ["AWS Solutions Architect", "CKA"],
};

const LOADING_RE =
  /Summary still loading|still loading|Loading…|Loading\.\.\.|Caricamento/i;

/** Human-followable defaults (ms). */
export const PACE = {
  afterNav: 2500,
  afterClick: 1200,
  afterFill: 800,
  read: 2800,
  scroll: 900,
  caption: 400,
};

export function sleep(ms) {
  return new Promise((r) => setTimeout(r, ms));
}

export async function caption(page, text) {
  await page.evaluate((t) => {
    let el = document.getElementById("docs-tour-caption");
    if (!el) {
      el = document.createElement("div");
      el.id = "docs-tour-caption";
      el.setAttribute("aria-live", "polite");
      el.style.cssText = [
        "position:fixed",
        "bottom:28px",
        "left:50%",
        "transform:translateX(-50%)",
        "z-index:2147483647",
        "background:rgba(15,23,42,0.92)",
        "color:#f8fafc",
        "padding:12px 20px",
        "border-radius:10px",
        "font:600 16px/1.35 ui-sans-serif,system-ui,sans-serif",
        "max-width:min(720px,88vw)",
        "text-align:center",
        "pointer-events:none",
        "box-shadow:0 8px 24px rgba(0,0,0,.25)",
      ].join(";");
      document.body.appendChild(el);
    }
    el.textContent = t;
  }, text);
  await sleep(PACE.caption);
}

export async function waitForData(page, { timeout = 90000 } = {}) {
  await page.waitForLoadState("domcontentloaded");
  await sleep(600);
  const deadline = Date.now() + timeout;
  while (Date.now() < deadline) {
    const busy = await page.evaluate((reSrc) => {
      const re = new RegExp(reSrc, "i");
      const text = document.body?.innerText || "";
      if (re.test(text)) return true;
      if (document.querySelector('[aria-busy="true"]')) return true;
      return false;
    }, LOADING_RE.source);
    if (!busy) {
      await sleep(800);
      const still = await page.evaluate(
        (reSrc) => new RegExp(reSrc, "i").test(document.body?.innerText || ""),
        LOADING_RE.source,
      );
      if (!still) return;
    }
    await sleep(400);
  }
}

export async function gotoPath(page, path, title) {
  const url = `${BASE}/${LOCALE}${path === "/" ? "" : path}`;
  if (title) await caption(page, title);
  await page.goto(url, { waitUntil: "networkidle", timeout: 120000 });
  await waitForData(page);
  await sleep(PACE.afterNav);
}

export async function softClick(page, locator, label) {
  const loc =
    typeof locator === "string"
      ? page.getByRole("button", { name: new RegExp(locator, "i") }).first()
      : locator;
  if ((await loc.count()) === 0) return false;
  try {
    await loc.scrollIntoViewIfNeeded();
    await loc.hover({ timeout: 5000 }).catch(() => {});
    await sleep(350);
    await loc.click({ timeout: 8000 });
    if (label) await caption(page, label);
    await sleep(PACE.afterClick);
    return true;
  } catch {
    return false;
  }
}

export async function softRadio(page, name, label) {
  const loc = page.getByRole("radio", { name: new RegExp(`^${name}$`, "i") });
  return softClick(page, loc, label);
}

export async function scrollDown(page, px = 420) {
  await page.mouse.wheel(0, px);
  await sleep(PACE.scroll);
}

/**
 * Pick the real scroll root: document, or the tallest overflow container.
 * (mouse.wheel is unreliable in headless Chromium — we drive scrollTop directly.)
 */
async function resolveScrollTarget(page) {
  return page.evaluate(() => {
    const doc = document.scrollingElement || document.documentElement;
    const candidates = [doc, ...document.querySelectorAll("main, [data-scroll], .overflow-y-auto, .overflow-auto")];
    let best = doc;
    let bestOverflow = Math.max(0, doc.scrollHeight - doc.clientHeight);
    for (const el of candidates) {
      if (!(el instanceof HTMLElement)) continue;
      const style = getComputedStyle(el);
      const oy = style.overflowY;
      const canScroll =
        el === doc ||
        oy === "auto" ||
        oy === "scroll" ||
        oy === "overlay";
      if (!canScroll) continue;
      const overflow = el.scrollHeight - el.clientHeight;
      if (overflow > bestOverflow + 40) {
        best = el;
        bestOverflow = overflow;
      }
    }
    // Mark for repeated evaluate
    best.setAttribute("data-docs-scroll-root", "1");
    return {
      overflow: bestOverflow,
      tag: best.tagName,
      id: best.id || "",
    };
  });
}

/**
 * Human-paced scroll from top to absolute bottom (visible in video).
 */
export async function scrollPageToEnd(
  page,
  {
    step = 360,
    pauseMs = 1100,
    maxSteps = 80,
    label = "Scroll to end of page",
  } = {},
) {
  await caption(page, label);
  await sleep(400);

  // Start from top so the tour always shows the full page
  await page.evaluate(() => {
    const el = document.scrollingElement || document.documentElement;
    el.scrollTo({ top: 0, behavior: "instant" });
    window.scrollTo(0, 0);
  });
  await sleep(500);

  const info = await resolveScrollTarget(page);
  if (!info.overflow || info.overflow < 24) {
    // Still try PageDown a few times in case layout settles late
    for (let i = 0; i < 4; i++) {
      await page.keyboard.press("PageDown");
      await sleep(pauseMs);
    }
    await sleep(PACE.read);
    return;
  }

  let lastY = -1;
  for (let i = 0; i < maxSteps; i++) {
    const state = await page.evaluate((stepPx) => {
      const el =
        document.querySelector("[data-docs-scroll-root='1']") ||
        document.scrollingElement ||
        document.documentElement;
      const maxY = Math.max(0, el.scrollHeight - el.clientHeight);
      const next = Math.min(maxY, el.scrollTop + stepPx);
      el.scrollTop = next;
      // Keep window in sync when scrolling document
      if (el === document.documentElement || el === document.body || el === document.scrollingElement) {
        window.scrollTo(0, next);
      }
      return {
        y: el.scrollTop,
        max: maxY,
        atBottom: el.scrollTop >= maxY - 8,
      };
    }, step);

    if (state.atBottom || state.max <= 0) break;
    if (state.y === lastY) {
      // Force jump remaining distance once, then stop
      await page.evaluate(() => {
        const el =
          document.querySelector("[data-docs-scroll-root='1']") ||
          document.scrollingElement ||
          document.documentElement;
        el.scrollTop = el.scrollHeight;
        window.scrollTo(0, el.scrollHeight);
      });
      break;
    }
    lastY = state.y;
    await sleep(pauseMs);
  }

  await caption(page, "End of page — footer");
  // Hold on footer credit so the video shows “Created by …”
  await page
    .getByRole("contentinfo")
    .scrollIntoViewIfNeeded()
    .catch(() => {});
  await sleep(PACE.read + 800);
}

export async function seedProfile(context) {
  await context.addInitScript((profile) => {
    localStorage.setItem("fmi:userProfile:v1", JSON.stringify(profile));
  }, DEMO_PROFILE);
}

export function convertWebmToMp4(webmPath, mp4Path) {
  const r = spawnSync(
    "ffmpeg",
    [
      "-y",
      "-i",
      webmPath,
      "-c:v",
      "libx264",
      "-preset",
      "medium",
      "-crf",
      "28",
      "-pix_fmt",
      "yuv420p",
      "-movflags",
      "+faststart",
      "-an",
      mp4Path,
    ],
    { encoding: "utf8" },
  );
  if (r.status !== 0) {
    throw new Error(`ffmpeg failed: ${r.stderr?.slice(-400) || r.status}`);
  }
}

/**
 * Record one tour: open context with video, run steps, save mp4.
 * @param {{ outDir: string, fileBase: string, seed?: boolean, run: (page) => Promise<void> }} opts
 */
export async function recordTour({ outDir, fileBase, seed = true, run }) {
  mkdirSync(outDir, { recursive: true });
  const tmpDir = join(outDir, `.tmp-${fileBase}`);
  mkdirSync(tmpDir, { recursive: true });

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1440, height: 900 },
    deviceScaleFactor: 1,
    recordVideo: { dir: tmpDir, size: { width: 1440, height: 900 } },
  });
  if (seed) await seedProfile(context);
  const page = await context.newPage();

  try {
    await run(page);
    await caption(page, "End of tour");
    await sleep(1800);
  } finally {
    await context.close();
    await browser.close();
  }

  const webms = readdirSync(tmpDir).filter((f) => f.endsWith(".webm"));
  if (!webms.length) throw new Error(`No webm for ${fileBase}`);
  const webmPath = join(tmpDir, webms[0]);
  const mp4Path = join(outDir, `${fileBase}.mp4`);
  convertWebmToMp4(webmPath, mp4Path);
  // cleanup tmp
  for (const f of readdirSync(tmpDir)) {
    try {
      unlinkSync(join(tmpDir, f));
    } catch {
      /* ignore */
    }
  }
  try {
    const { rmdirSync } = await import("node:fs");
    rmdirSync(tmpDir);
  } catch {
    /* ignore */
  }
  if (!existsSync(mp4Path)) throw new Error(`Missing ${mp4Path}`);
  return mp4Path;
}
