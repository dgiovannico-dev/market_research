import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { compareSortValues, sortRows } from "./tableSort.ts";

describe("tableSort", () => {
  it("compares numbers with nulls last", () => {
    assert.equal(compareSortValues(1, 2, "asc") < 0, true);
    assert.equal(compareSortValues(null, 1, "asc") > 0, true);
    assert.equal(compareSortValues(1, null, "desc") < 0, true);
  });

  it("sorts rows stably", () => {
    const rows = [
      { name: "b", n: 1 },
      { name: "a", n: 2 },
      { name: "c", n: 1 },
    ];
    const byN = sortRows(rows, (r) => r.n, "asc");
    assert.deepEqual(
      byN.map((r) => r.name),
      ["b", "c", "a"],
    );
  });
});
