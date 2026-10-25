import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { nextCountriesOnClick } from "./toggleCountrySelection.ts";

describe("nextCountriesOnClick", () => {
  it("selects a single country", () => {
    assert.deepEqual(nextCountriesOnClick([], "it"), ["IT"]);
  });

  it("replaces a previous selection", () => {
    assert.deepEqual(nextCountriesOnClick(["CH", "DE"], "it"), ["IT"]);
  });

  it("toggles off when clicking the sole selected country", () => {
    assert.deepEqual(nextCountriesOnClick(["IT"], "IT"), []);
  });

  it("ignores empty / unknown", () => {
    assert.deepEqual(nextCountriesOnClick(["IT"], ""), ["IT"]);
    assert.deepEqual(nextCountriesOnClick(["IT"], "unknown"), ["IT"]);
  });
});
