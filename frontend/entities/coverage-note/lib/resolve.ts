import type { CoverageNote, CoverageNotesSource } from "../model";

export function coverageNoteKey(note: CoverageNote): string {
  if (typeof note === "string") return note;
  return note.code
    ? `${note.code}:${note.thin_n ?? ""}:${note.pct ?? ""}:${note.sources ?? ""}`
    : note.message ?? JSON.stringify(note);
}

/** Collect top-level notes, or merge nested market/focus when lens=compare. */
export function resolveCoverageNotes(
  payload: CoverageNotesSource | null | undefined,
): CoverageNote[] {
  if (!payload) return [];
  if (payload.coverage_notes?.length) return payload.coverage_notes;
  const out: CoverageNote[] = [];
  const seen = new Set<string>();
  for (const note of [
    ...(payload.market?.coverage_notes ?? []),
    ...(payload.focus?.coverage_notes ?? []),
  ]) {
    const key = coverageNoteKey(note);
    if (seen.has(key)) continue;
    seen.add(key);
    out.push(note);
  }
  return out;
}
