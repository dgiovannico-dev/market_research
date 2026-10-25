/** Pure pick/limit for rising-vs-cooling skill charts (Mostra = total bars). */

export type RiseCoolSourceItem = {
  technology: string;
  growth_pct: number | null;
  sample_size: number;
  recent_mentions: number;
  previous_mentions: number;
  status: string;
};

export type RiseCoolRow = {
  technology: string;
  growth_pct: number;
  sample_size: number;
  recent_mentions: number;
  previous_mentions: number;
  side: "rise" | "cool";
};

function toRow(
  it: RiseCoolSourceItem,
  side: "rise" | "cool",
): RiseCoolRow {
  return {
    technology: it.technology,
    growth_pct: it.growth_pct as number,
    sample_size: it.sample_size,
    recent_mentions: it.recent_mentions,
    previous_mentions: it.previous_mentions,
    side,
  };
}

/** Mostra N → floor(N/2) rise slots + ceil(N/2) cool slots (strict, no cross-fill). */
export function riseCoolSlotTargets(topN: number): {
  riseSlots: number;
  coolSlots: number;
} {
  const limit = Math.max(0, Math.floor(topN));
  const riseSlots = Math.floor(limit / 2);
  return { riseSlots, coolSlots: limit - riseSlots };
}

/**
 * Select up to `topN` chartable skills, balanced rise/cool.
 * Odd topN: cool gets the extra slot (floor(n/2) rise, ceil(n/2) cool).
 * Does not backfill from the other side — empty cooling stays empty so Mostra
 * means “half each”, not “fill N bars from whichever side has data”.
 */
export function pickRiseCoolRows(
  items: RiseCoolSourceItem[],
  topN: number,
): RiseCoolRow[] {
  const limit = Math.max(0, Math.floor(topN));
  if (limit === 0) return [];

  const ok = items.filter(
    (it) =>
      it.status === "ok" &&
      typeof it.growth_pct === "number" &&
      Number.isFinite(it.growth_pct),
  );
  const rising = ok
    .filter((it) => (it.growth_pct as number) > 0)
    .sort((a, b) => (b.growth_pct as number) - (a.growth_pct as number));
  const cooling = ok
    .filter((it) => (it.growth_pct as number) <= 0)
    .sort((a, b) => (a.growth_pct as number) - (b.growth_pct as number));

  const { riseSlots, coolSlots } = riseCoolSlotTargets(limit);
  const risePick = rising.slice(0, riseSlots);
  const coolPick = cooling.slice(0, coolSlots);

  // Chart order: cooling (most negative at bottom of category axis first)
  // then rising reversed so strongest rise ends at top.
  return [
    ...coolPick.map((it) => toRow(it, "cool")),
    ...risePick
      .slice()
      .reverse()
      .map((it) => toRow(it, "rise")),
  ];
}

/** Corpus-level n for the footer — all ok items, not the Mostra slice. */
export function riseCoolCorpusSampleSize(items: RiseCoolSourceItem[]): number {
  return items
    .filter((it) => it.status === "ok")
    .reduce((sum, it) => sum + (it.sample_size || 0), 0);
}
