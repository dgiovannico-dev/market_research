import assert from "node:assert/strict";
import { describe, it } from "node:test";
import {
  filterRows,
  joinSearchParts,
  normalizeFilterQuery,
  rowMatchesFilter,
} from "./tableFilter.ts";

describe("tableFilter", () => {
  it("normalizes query", () => {
    assert.equal(normalizeFilterQuery("  React  "), "react");
  });

  it("matches substring case-insensitively", () => {
    assert.equal(rowMatchesFilter("React TypeScript", "react"), true);
    assert.equal(rowMatchesFilter("React TypeScript", "python"), false);
  });

  it("filters rows via haystack", () => {
    const rows = [{ name: "React" }, { name: "Vue" }];
    assert.deepEqual(
      filterRows(rows, "re", (r) => r.name).map((r) => r.name),
      ["React"],
    );
  });

  it("returns all rows when query empty", () => {
    const rows = [{ name: "A" }];
    assert.equal(filterRows(rows, "", (r) => r.name).length, 1);
  });

  it("joinSearchParts joins defined parts", () => {
    assert.equal(joinSearchParts("a", null, "b", undefined), "a b");
  });
});
