import assert from "node:assert/strict";
import { describe, it } from "node:test";
import {
  jobsUrlFiltersEqual,
  parseCsvList,
  parseJobsUrlFilters,
  toResearchJobsParams,
  writeJobsFiltersToSearchParams,
} from "./jobsListParams.ts";

describe("parseCsvList", () => {
  it("splits and trims", () => {
    assert.deepEqual(parseCsvList("IT, CH, "), ["IT", "CH"]);
    assert.deepEqual(parseCsvList(null), []);
  });
});

describe("parseJobsUrlFilters", () => {
  it("prefers UI keys and falls back to API aliases", () => {
    const fromUi = parseJobsUrlFilters((k) =>
      ({ countries: "it,ch", sources: "1,2", q: "react" } as Record<string, string>)[k] ??
      null,
    );
    assert.equal(fromUi.q, "react");
    assert.deepEqual(fromUi.countries, ["it", "ch"]);
    assert.deepEqual(fromUi.sources, ["1", "2"]);

    const fromLegacy = parseJobsUrlFilters((k) =>
      ({ country_code: "DE", source_id: "9", technology: "go" } as Record<
        string,
        string
      >)[k] ?? null,
    );
    assert.equal(fromLegacy.q, "go");
    assert.deepEqual(fromLegacy.countries, ["DE"]);
    assert.deepEqual(fromLegacy.sources, ["9"]);
  });
});

describe("toResearchJobsParams", () => {
  it("maps URL CSV fields to API param names", () => {
    const params = toResearchJobsParams({
      q: "python",
      countriesCsv: "IT,CH",
      sourcesCsv: "3,4",
      contractsCsv: "freelance",
      remotesCsv: "remote",
      lens: "focus",
      queryIds: [12, 99],
      sort: "title",
      order: "asc",
      skip: 25,
      limit: 25,
    });
    assert.deepEqual(params, {
      q: "python",
      lens: "focus",
      query_id: 12,
      country_code: "IT,CH",
      source_id: "3,4",
      contract_type: "freelance",
      remote_type: "remote",
      sort: "title",
      order: "asc",
      skip: 25,
      limit: 25,
    });
  });

  it("omits empty filters and query_id when none", () => {
    const params = toResearchJobsParams({
      q: "",
      countriesCsv: "",
      sourcesCsv: "",
      contractsCsv: "",
      remotesCsv: "",
      lens: "market",
      queryIds: [],
      sort: "published_at",
      order: "desc",
      skip: 0,
      limit: 25,
    });
    assert.equal(params.q, undefined);
    assert.equal(params.country_code, undefined);
    assert.equal(params.query_id, undefined);
  });
});

describe("writeJobsFiltersToSearchParams", () => {
  it("writes UI keys, clears page and legacy aliases", () => {
    const params = new URLSearchParams(
      "page=3&country_code=XX&technology=old&source_id=1&q=keep",
    );
    writeJobsFiltersToSearchParams(
      params,
      {
        q: "rust",
        countries: ["it", "ch"],
        sources: ["5"],
        contracts: [],
        remotes: ["hybrid"],
      },
      { lens: "focus", queryIds: [7] },
    );
    assert.equal(params.get("page"), null);
    assert.equal(params.get("country_code"), null);
    assert.equal(params.get("technology"), null);
    assert.equal(params.get("source_id"), null);
    assert.equal(params.get("q"), "rust");
    assert.equal(params.get("countries"), "IT,CH");
    assert.equal(params.get("sources"), "5");
    assert.equal(params.get("remotes"), "hybrid");
    assert.equal(params.has("contracts"), false);
    assert.equal(params.get("lens"), "focus");
    assert.equal(params.get("query_ids"), "7");
  });

  it("clears all filters on empty state", () => {
    const params = new URLSearchParams(
      "q=x&countries=IT&sources=1&contracts=c&remotes=r&page=2&lens=focus",
    );
    writeJobsFiltersToSearchParams(
      params,
      { q: "", countries: [], sources: [], contracts: [], remotes: [] },
      { lens: "market", queryIds: [] },
    );
    assert.equal(params.toString(), "");
  });
});

describe("jobsUrlFiltersEqual", () => {
  it("compares field-wise", () => {
    const a = {
      q: "a",
      countries: ["IT"],
      sources: [],
      contracts: [],
      remotes: [],
    };
    assert.equal(jobsUrlFiltersEqual(a, { ...a }), true);
    assert.equal(jobsUrlFiltersEqual(a, { ...a, countries: ["CH"] }), false);
  });
});
