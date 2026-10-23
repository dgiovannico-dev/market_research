import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { withLensQuery } from "./query.ts";

describe("withLensQuery", () => {
  it("returns path unchanged when no params", () => {
    assert.equal(withLensQuery("/api/v1/market/summary", {}), "/api/v1/market/summary");
  });

  it("omits null empty and undefined params", () => {
    const url = withLensQuery("/x", {
      days: 30,
      skip: "",
      nada: null,
      miss: undefined,
    });
    assert.equal(url, "/x?days=30");
  });

  it("appends lens query_ids and country_code", () => {
    const url = withLensQuery(
      "/api/v1/market/trends",
      { days: 90 },
      "focus",
      [1, 2],
      ["IT", "CH"],
    );
    assert.ok(url.startsWith("/api/v1/market/trends?"));
    const qs = new URLSearchParams(url.split("?")[1]);
    assert.equal(qs.get("days"), "90");
    assert.equal(qs.get("lens"), "focus");
    assert.equal(qs.get("query_ids"), "1,2");
    assert.equal(qs.get("country_code"), "IT,CH");
  });

  it("omits empty queryIds and countries arrays", () => {
    const url = withLensQuery("/x", { days: 7 }, "market", [], []);
    assert.equal(url, "/x?days=7&lens=market");
  });
});
