import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { buildTechGraph, egoNeighbors } from "./buildTechGraph.ts";

const pairs = [
  { tech_a: "Python", tech_b: "LLM", support: 40, lift: 2.1 },
  { tech_a: "Python", tech_b: "RAG", support: 30, lift: 1.8 },
  { tech_a: "Java", tech_b: "Spring Boot", support: 50, lift: 3.0 },
  { tech_a: "Python", tech_b: "FastAPI", support: 20, lift: 1.5 },
];

describe("buildTechGraph", () => {
  it("keeps top-N nodes by weight and edges among them", () => {
    const g = buildTechGraph(pairs, 4);
    assert.equal(g.nodes.length, 4);
    assert.ok(g.nodes.some((n) => n.id === "Java"));
    assert.ok(g.links.some((l) => l.source === "Java" || l.target === "Java"));
  });

  it("always keeps seed and fills neighbors", () => {
    const g = buildTechGraph(pairs, 3, "Python");
    assert.equal(g.nodes[0]?.id, "Python");
    assert.equal(g.nodes.length, 3);
    assert.ok(g.nodes.every((n) => n.id === "Python" || ["LLM", "RAG", "FastAPI"].includes(n.id)));
    assert.ok(!g.nodes.some((n) => n.id === "Java"));
  });

  it("returns empty for maxNodes 0", () => {
    assert.deepEqual(buildTechGraph(pairs, 0), { nodes: [], links: [] });
  });
});

describe("egoNeighbors", () => {
  it("ranks co-mentioned techs by support", () => {
    const rows = egoNeighbors(pairs, "Python", 2);
    assert.equal(rows.length, 2);
    assert.equal(rows[0].label, "LLM");
    assert.equal(rows[0].value, 40);
    assert.equal(rows[1].label, "RAG");
  });

  it("matches seed case-insensitively", () => {
    const rows = egoNeighbors(pairs, "python", 2);
    assert.equal(rows.length, 2);
    assert.equal(rows[0].label, "LLM");
    const g = buildTechGraph(pairs, 3, "PYTHON");
    assert.equal(g.nodes[0]?.id, "Python");
  });
});
