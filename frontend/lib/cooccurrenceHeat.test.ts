import assert from "node:assert/strict";
import { describe, it } from "node:test";
import {
  buildCooccurrenceHeat,
  languageCountryCellsToHeat,
  roleTechCellsToHeat,
  seniorityTechCellsToHeat,
  techCountryCellsToHeat,
} from "../widgets/relations-dashboard/ui/cooccurrenceHeat.ts";

describe("buildCooccurrenceHeat", () => {
  it("ranks labels by support and emits symmetric cells", () => {
    const { labels, values } = buildCooccurrenceHeat(
      [
        { tech_a: "Java", tech_b: "Spring", support: 10 },
        { tech_a: "Java", tech_b: "Kotlin", support: 5 },
        { tech_a: "Go", tech_b: "Docker", support: 1 },
      ],
      3,
    );
    assert.equal(labels[0], "Java");
    assert.ok(labels.includes("Spring"));
    assert.ok(labels.includes("Kotlin"));
    assert.ok(!labels.includes("Go"));
    const javaSpring = values.find(
      ([xi, yi, v]) =>
        v === 10 &&
        ((labels[xi] === "Java" && labels[yi] === "Spring") ||
          (labels[xi] === "Spring" && labels[yi] === "Java")),
    );
    assert.ok(javaSpring);
  });
});

describe("techCountryCellsToHeat", () => {
  it("maps cells to x=country y=tech indices", () => {
    const values = techCountryCellsToHeat(
      ["Java", "Go"],
      ["CH", "DE"],
      [
        { technology: "Java", country_code: "CH", jobs: 4 },
        { technology: "Go", country_code: "DE", jobs: 2 },
      ],
    );
    assert.deepEqual(values.sort(), [
      [0, 0, 4],
      [1, 1, 2],
    ].sort());
  });
});

describe("languageCountryCellsToHeat", () => {
  it("maps cells to x=country y=language indices", () => {
    const values = languageCountryCellsToHeat(
      ["en", "de"],
      ["CH", "DE"],
      [
        { language: "en", country_code: "CH", jobs: 7 },
        { language: "de", country_code: "DE", jobs: 3 },
      ],
    );
    assert.deepEqual(values.sort(), [
      [0, 0, 7],
      [1, 1, 3],
    ].sort());
  });
});

describe("roleTechCellsToHeat", () => {
  it("maps cells to x=technology y=role_family indices", () => {
    const values = roleTechCellsToHeat(
      ["Backend", "Frontend"],
      ["Java", "React"],
      [
        { role_family: "Backend", technology: "Java", jobs: 9 },
        { role_family: "Frontend", technology: "React", jobs: 5 },
      ],
    );
    assert.deepEqual(values.sort(), [
      [0, 0, 9],
      [1, 1, 5],
    ].sort());
  });
});

describe("seniorityTechCellsToHeat", () => {
  it("maps cells to x=technology y=seniority indices", () => {
    const values = seniorityTechCellsToHeat(
      ["senior", "mid"],
      ["Java", "React"],
      [
        { seniority: "senior", technology: "Java", jobs: 9 },
        { seniority: "mid", technology: "React", jobs: 5 },
      ],
    );
    assert.deepEqual(values.sort(), [
      [0, 0, 9],
      [1, 1, 5],
    ].sort());
  });
});
