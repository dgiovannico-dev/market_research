import { describe, expect, it } from "vitest";
import { canSeeAdminConfig } from "./adminUi";

describe("canSeeAdminConfig", () => {
  it("hides panels for non-admin when OIDC is on", () => {
    expect(canSeeAdminConfig({ enabled: true, isAdmin: false })).toBe(false);
  });

  it("shows panels for admin when OIDC is on", () => {
    expect(canSeeAdminConfig({ enabled: true, isAdmin: true })).toBe(true);
  });

  it("shows panels when OIDC is off (local ops token path)", () => {
    expect(canSeeAdminConfig({ enabled: false, isAdmin: false })).toBe(true);
  });
});
