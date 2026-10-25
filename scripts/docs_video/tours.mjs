/**
 * Human-paced tour definitions covering all Atlas zones.
 * After each page loads, scroll through content until page end.
 */
import {
  caption,
  gotoPath,
  softClick,
  softRadio,
  scrollPageToEnd,
  sleep,
  waitForData,
  PACE,
} from "./lib.mjs";

async function visit(page, path, title) {
  await gotoPath(page, path, title);
  await scrollPageToEnd(page, { label: `Scroll · ${title}` });
}

async function periodAndLens(page) {
  await softRadio(page, "14 d", "Period: last 14 days");
  await waitForData(page);
  await sleep(PACE.read);
  await softRadio(page, "30 d", "Back to 30 days");
  await waitForData(page);
  await softClick(
    page,
    page.getByRole("button", { name: /Focus\./i }),
    "Lens: Focus (personal intents)",
  );
  await waitForData(page);
  await sleep(PACE.read);
  await softClick(
    page,
    page.getByRole("button", { name: /Market\./i }),
    "Lens: Market (broad scan)",
  );
  await waitForData(page);
}

async function showHowToRead(page) {
  const btn = page.getByRole("button", { name: /How to read/i }).first();
  if ((await btn.count()) === 0) return;
  await softClick(page, btn, "Open “How to read”");
  await sleep(PACE.read);
  await softClick(page, btn, "Hide “How to read”");
}

async function showTableToggle(page) {
  const btn = page.getByRole("button", { name: /Show table/i }).first();
  if ((await btn.count()) === 0) return;
  await softClick(page, btn, "Switch chart → table");
  await sleep(PACE.read);
  const chart = page.getByRole("button", { name: /Show chart/i }).first();
  if ((await chart.count()) > 0) {
    await softClick(page, chart, "Back to chart");
  }
}

/** Explore zone — Demand Compass + market analytics. */
export async function tourExplore(page) {
  await gotoPath(page, "/", "Explore · Executive Demand Compass");
  await periodAndLens(page);
  await showHowToRead(page);
  await scrollPageToEnd(page, { label: "Scroll · Executive full page" });
  await softClick(
    page,
    page.getByRole("link", { name: /Open trends/i }),
    "Jump to Technology Trends",
  );
  await waitForData(page);
  await sleep(PACE.read);
  await scrollPageToEnd(page, { label: "Scroll · Trends (from executive link)" });

  await visit(page, "/market-scan", "Market scan · discovery probes");

  await gotoPath(page, "/explorer", "Explorer · search stored jobs");
  const search = page.getByPlaceholder(/search|query|filter/i).first();
  if ((await search.count()) > 0) {
    await search.click();
    await search.fill("python");
    await sleep(PACE.afterFill);
    await softClick(
      page,
      page.getByRole("button", { name: /search|apply|filter/i }).first(),
      "Run explorer search",
    );
    await waitForData(page);
    await sleep(PACE.read);
  }
  await scrollPageToEnd(page, { label: "Scroll · Explorer results" });

  await gotoPath(page, "/trends", "Trends · rising vs cooling");
  await showTableToggle(page);
  await scrollPageToEnd(page, { label: "Scroll · Trends full page" });

  await visit(page, "/skills", "Skills · observed technology ranks");
  await visit(page, "/relations", "Relations · co-occurrence matrices");
  await visit(page, "/rates", "Rates · advertised pay signals");
  await visit(page, "/countries", "Countries · geographic coverage");
  await visit(page, "/languages", "Languages · languages in ads");
  await visit(page, "/certifications", "Certifications · corpus + benchmarks");
  await visit(page, "/stack", "Stack Compass · learning candidates");
}

/** Jobs zone — list, profile gaps, study plan, applications. */
export async function tourJobs(page) {
  await gotoPath(page, "/jobs", "Jobs · Job Explorer (DB-only)");
  await softClick(
    page,
    page.getByRole("button", { name: /Apply filters/i }),
    "Apply filters (Any × Any)",
  );
  await waitForData(page);
  await sleep(PACE.read);

  const search = page.getByPlaceholder(/Search/i).first();
  if ((await search.count()) > 0) {
    await search.fill("kubernetes");
    await sleep(PACE.afterFill);
    await softClick(
      page,
      page.getByRole("button", { name: /Apply filters/i }),
      "Filter jobs: kubernetes",
    );
    await waitForData(page);
    await sleep(PACE.read);
  }
  await scrollPageToEnd(page, { label: "Scroll · Jobs list to end" });

  await gotoPath(page, "/profile", "Profile · local skills (browser only)");
  await softClick(
    page,
    page.getByRole("button", { name: /Save & analyze gaps/i }),
    "Save & analyze skill gaps",
  );
  await waitForData(page);
  await sleep(PACE.read);
  await page
    .getByText(/Priority skill gaps/i)
    .scrollIntoViewIfNeeded()
    .catch(() => {});
  await sleep(PACE.read);
  await scrollPageToEnd(page, { label: "Scroll · Profile + gaps" });

  await gotoPath(page, "/learn", "Study Advisor · plan from Stack evidence");
  await softClick(
    page,
    page.getByRole("button", { name: /Generate plan/i }),
    "Generate study plan",
  );
  await waitForData(page);
  await sleep(PACE.read);
  await scrollPageToEnd(page, { label: "Scroll · Study plan" });

  await visit(page, "/applications", "Applications · track outreach");
}

/** Ops zone — quality KPIs, sources catalog, alerts. */
export async function tourOps(page) {
  await visit(page, "/quality", "Ops · Data quality KPIs");
  await visit(page, "/sources", "Ops · Sources & LLM runtime");
  await caption(page, "Demo stops before credentialed / paid runs");
  await sleep(PACE.read);
  await visit(page, "/alerts", "Ops · Alerts & watch signals");
}

/** Research zone — focus intents, weekly report, assistant. */
export async function tourResearch(page) {
  await gotoPath(page, "/focus", "Research · My focus intents");
  await sleep(PACE.read);
  const label = page.getByLabel(/Label/i).first();
  if ((await label.count()) > 0) {
    await label.fill("Demo: React TypeScript remote");
    await sleep(PACE.afterFill);
    const q = page.getByLabel(/Query text/i).first();
    if ((await q.count()) > 0) {
      await q.fill("freelance React TypeScript remote");
      await sleep(PACE.afterFill);
    }
    await caption(page, "Form filled — not saved (demo)");
    await sleep(PACE.read);
  }
  await scrollPageToEnd(page, { label: "Scroll · Focus page" });

  await visit(page, "/report", "Research · Weekly / period report");

  await gotoPath(page, "/assistant", "Research · Assistant briefs");
  await sleep(PACE.read);
  const gen = page
    .getByRole("button", { name: /Generate|Ask|Run brief|Create/i })
    .first();
  if ((await gen.count()) > 0 && !(await gen.isDisabled().catch(() => true))) {
    await softClick(page, gen, "Request a brief (may stub without LLM)");
    await waitForData(page);
    await sleep(PACE.read);
  }
  await scrollPageToEnd(page, { label: "Scroll · Assistant" });
}

/** Single continuous walkthrough of the whole product. */
export async function tourFullPlatform(page) {
  await caption(page, "FMI full platform tour — follow along");
  await sleep(1500);
  await tourExplore(page);
  await tourJobs(page);
  await tourOps(page);
  await tourResearch(page);
  await caption(page, "That’s the full Atlas walkthrough");
  await sleep(2000);
}
