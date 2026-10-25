import assert from "node:assert/strict";
import { describe, it } from "node:test";
import {
  pickRiseCoolRows,
  riseCoolCorpusSampleSize,
  riseCoolSlotTargets,
  type RiseCoolSourceItem,
} from "./riseCoolPick.ts";

function item(
  technology: string,
  growth_pct: number,
  sample_size = 10,
): RiseCoolSourceItem {
  return {
    technology,
    growth_pct,
    sample_size,
    recent_mentions: 5,
    previous_mentions: 5,
    status: "ok",
  };
}

describe("pickRiseCoolRows", () => {
  const pool = [
    item("A", 80),
    item("B", 60),
    item("C", 40),
    item("D", 20),
    item("D2", 15),
    item("D3", 10),
    item("E", -10),
    item("F", -30),
    item("G", -50),
    item("H", -70),
    item("H2", -80),
    item("H3", -90),
  ];

  it("respects exact topN for even Mostra (5+5)", () => {
    const rows = pickRiseCoolRows(pool, 10);
    assert.equal(rows.length, 10);
    assert.equal(rows.filter((r) => r.side === "rise").length, 5);
    assert.equal(rows.filter((r) => r.side === "cool").length, 5);
  });

  it("respects exact topN for odd Mostra (2 rise + 3 cool)", () => {
    const rows = pickRiseCoolRows(pool, 5);
    assert.equal(rows.length, 5);
    assert.equal(rows.filter((r) => r.side === "rise").length, 2);
    assert.equal(rows.filter((r) => r.side === "cool").length, 3);
  });

  it("does not backfill when one side is thin (strict half)", () => {
    const thinRise = [
      item("OnlyRise", 50),
      item("C1", -10),
      item("C2", -20),
      item("C3", -30),
      item("C4", -40),
      item("C5", -50),
    ];
    const rows = pickRiseCoolRows(thinRise, 6);
    assert.equal(rows.length, 4);
    assert.equal(rows.filter((r) => r.side === "rise").length, 1);
    assert.equal(rows.filter((r) => r.side === "cool").length, 3);
    assert.deepEqual(riseCoolSlotTargets(6), { riseSlots: 3, coolSlots: 3 });
  });

  it("leaves cool empty when corpus has only rising", () => {
    const onlyRise = [item("A", 80), item("B", 60), item("C", 40), item("D", 20)];
    const rows = pickRiseCoolRows(onlyRise, 10);
    assert.equal(rows.length, 4);
    assert.equal(rows.filter((r) => r.side === "rise").length, 4);
    assert.equal(rows.filter((r) => r.side === "cool").length, 0);
  });

  it("ignores non-ok and null growth", () => {
    const mixed: RiseCoolSourceItem[] = [
      item("Ok", 10),
      { ...item("Thin", 99), status: "thin" },
      { ...item("Null", 0), growth_pct: null },
      item("Cool", -5),
    ];
    const rows = pickRiseCoolRows(mixed, 10);
    assert.equal(rows.length, 2);
    assert.deepEqual(
      rows.map((r) => r.technology).sort(),
      ["Cool", "Ok"],
    );
  });

  it("returns empty for topN 0", () => {
    assert.deepEqual(pickRiseCoolRows(pool, 0), []);
  });
});

describe("riseCoolCorpusSampleSize", () => {
  it("sums all ok sample sizes, not a Mostra slice", () => {
    const items = [item("A", 10, 100), item("B", -5, 50), { ...item("X", 1, 999), status: "thin" }];
    assert.equal(riseCoolCorpusSampleSize(items), 150);
  });
});
