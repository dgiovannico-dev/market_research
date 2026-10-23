import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { formatDateMinute } from "./formatDateTime.ts";

describe("formatDateMinute", () => {
  it("truncates ISO datetimes to the minute in UTC", () => {
    assert.equal(
      formatDateMinute("2026-10-20T23:42:54.394978+00:00"),
      "2026-10-20 23:42 UTC",
    );
    assert.equal(formatDateMinute("2026-10-20T23:42:54Z"), "2026-10-20 23:42 UTC");
  });

  it("keeps date-only strings as dates", () => {
    assert.equal(formatDateMinute("2026-10-20"), "2026-10-20");
  });

  it("returns fallback for empty values", () => {
    assert.equal(formatDateMinute(""), "—");
    assert.equal(formatDateMinute(null), "—");
    assert.equal(formatDateMinute(undefined), "—");
  });
});
