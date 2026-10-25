/** Build ECharts force-graph nodes/links from co-occurrence pairs. */

export type TechGraphPair = {
  tech_a: string;
  tech_b: string;
  support: number;
  lift?: number | null;
};

export type TechGraphNode = {
  id: string;
  name: string;
  /** Sum of support on incident edges (size cue). */
  value: number;
  category?: number;
};

export type TechGraphLink = {
  source: string;
  target: string;
  support: number;
  lift: number | null;
  /** Line width hint (normalized later in chart). */
  lineWidth: number;
};

export type TechGraph = {
  nodes: TechGraphNode[];
  links: TechGraphLink[];
};

/**
 * Keep top `maxNodes` technologies by incident support, then edges among them.
 * When `seed` is set, seed is always kept and neighbors fill remaining slots.
 */
export function buildTechGraph(
  pairs: TechGraphPair[],
  maxNodes: number,
  seed?: string | null,
): TechGraph {
  const limit = Math.max(0, Math.floor(maxNodes));
  if (limit === 0) return { nodes: [], links: [] };

  const weight = new Map<string, number>();
  const clean: TechGraphPair[] = [];
  for (const p of pairs) {
    const a = String(p.tech_a || "").trim();
    const b = String(p.tech_b || "").trim();
    const support = Number(p.support) || 0;
    if (!a || !b || a === b || support <= 0) continue;
    clean.push({
      tech_a: a,
      tech_b: b,
      support,
      lift: p.lift ?? null,
    });
    weight.set(a, (weight.get(a) ?? 0) + support);
    weight.set(b, (weight.get(b) ?? 0) + support);
  }

  const seedRaw = (seed || "").trim() || null;
  const seedKey = seedRaw ? seedRaw.toLowerCase() : null;
  // Prefer the label as it appears in pairs when casing differs from URL/input.
  let seedName: string | null = seedRaw;
  if (seedKey) {
    for (const p of clean) {
      if (p.tech_a.toLowerCase() === seedKey) {
        seedName = p.tech_a;
        break;
      }
      if (p.tech_b.toLowerCase() === seedKey) {
        seedName = p.tech_b;
        break;
      }
    }
  }
  let keep: string[];
  if (seedName && seedKey) {
    // Ego mode: only seed + direct neighbors by support on edges to seed.
    const neighborWeight = new Map<string, number>();
    for (const p of clean) {
      let other: string | null = null;
      if (p.tech_a.toLowerCase() === seedKey) other = p.tech_b;
      else if (p.tech_b.toLowerCase() === seedKey) other = p.tech_a;
      if (!other) continue;
      neighborWeight.set(
        other,
        Math.max(neighborWeight.get(other) ?? 0, p.support),
      );
    }
    const others = [...neighborWeight.entries()]
      .sort((x, y) => y[1] - x[1] || x[0].localeCompare(y[0]))
      .map(([name]) => name);
    keep = [seedName, ...others].slice(0, limit);
  } else {
    keep = [...weight.entries()]
      .sort((x, y) => y[1] - x[1] || x[0].localeCompare(y[0]))
      .slice(0, limit)
      .map(([name]) => name);
  }

  const keepSet = new Set(keep);
  const nodes: TechGraphNode[] = keep.map((name) => ({
    id: name,
    name,
    value: weight.get(name) ?? 0,
    category: seedName && name === seedName ? 0 : 1,
  }));

  const maxSupport = Math.max(1, ...clean.map((p) => p.support));
  const links: TechGraphLink[] = [];
  for (const p of clean) {
    if (!keepSet.has(p.tech_a) || !keepSet.has(p.tech_b)) continue;
    links.push({
      source: p.tech_a,
      target: p.tech_b,
      support: p.support,
      lift: typeof p.lift === "number" ? p.lift : null,
      lineWidth: 1 + (3 * p.support) / maxSupport,
    });
  }

  return { nodes, links };
}

/** Neighbors of seed sorted by support (other endpoint of each pair). */
export function egoNeighbors(
  pairs: TechGraphPair[],
  seed: string,
  limit: number,
): { label: string; value: number; lift: number | null }[] {
  const seedKey = seed.trim().toLowerCase();
  if (!seedKey || limit <= 0) return [];
  const byNeighbor = new Map<string, { support: number; lift: number | null }>();
  for (const p of pairs) {
    const a = String(p.tech_a || "").trim();
    const b = String(p.tech_b || "").trim();
    const support = Number(p.support) || 0;
    if (!a || !b || support <= 0) continue;
    let other: string | null = null;
    if (a.toLowerCase() === seedKey) other = b;
    else if (b.toLowerCase() === seedKey) other = a;
    if (!other) continue;
    const prev = byNeighbor.get(other);
    if (!prev || support > prev.support) {
      byNeighbor.set(other, {
        support,
        lift: typeof p.lift === "number" ? p.lift : null,
      });
    }
  }
  return [...byNeighbor.entries()]
    .sort((x, y) => y[1].support - x[1].support || x[0].localeCompare(y[0]))
    .slice(0, Math.floor(limit))
    .map(([label, v]) => ({
      label,
      value: v.support,
      lift: v.lift,
    }));
}
