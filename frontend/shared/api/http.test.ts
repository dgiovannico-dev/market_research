import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { ApiRequestError } from "./http.ts";

describe("ApiRequestError", () => {
  it("exposes status path and default message", () => {
    const err = new ApiRequestError("/api/v1/x", 503);
    assert.equal(err.name, "ApiRequestError");
    assert.equal(err.status, 503);
    assert.equal(err.path, "/api/v1/x");
    assert.match(err.message, /503/);
  });

  it("prefers detail string when provided", () => {
    const err = new ApiRequestError("/api/v1/x", 400, "bad lens");
    assert.equal(err.message, "bad lens");
  });
});
