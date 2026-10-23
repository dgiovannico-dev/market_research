import assert from "node:assert/strict";
import { describe, it } from "node:test";
import {
  catalogFiltersEqual,
  parseCatalogUrlFilters,
  writeCatalogFiltersToSearchParams,
} from "./catalogFilters.ts";

describe("parseCatalogUrlFilters", () => {
  it("reads status/category/kind from URL getters", () => {
    const state = parseCatalogUrlFilters(
      (k) =>
        ({ status: "ACTIVE", category: "A", kind: "free" } as Record<string, string>)[k] ??
        null,
    );
    assert.deepEqual(state, { status: "ACTIVE", category: "A", kind: "free" });
  });

  it("ignores unknown kind", () => {
    const state = parseCatalogUrlFilters((k) => (k === "kind" ? "paid" : null));
    assert.equal(state.kind, "");
  });
});

describe("writeCatalogFiltersToSearchParams", () => {
  it("writes and clears filter keys", () => {
    const params = new URLSearchParams("status=OLD&foo=1");
    writeCatalogFiltersToSearchParams(params, {
      status: "ACTIVE",
      category: "",
      kind: "credentialed",
    });
    assert.equal(params.get("status"), "ACTIVE");
    assert.equal(params.get("category"), null);
    assert.equal(params.get("kind"), "credentialed");
    assert.equal(params.get("foo"), "1");
  });
});

describe("catalogFiltersEqual", () => {
  it("compares field-wise", () => {
    const a = { status: "ACTIVE", category: "A", kind: "free" as const };
    assert.equal(catalogFiltersEqual(a, { ...a }), true);
    assert.equal(catalogFiltersEqual(a, { ...a, status: "" }), false);
  });
});
