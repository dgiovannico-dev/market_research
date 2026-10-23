"use client";

import { useTranslations } from "next-intl";
import {
  coverageNoteKey,
  resolveCoverageNotes,
  type CoverageNote,
} from "@/entities/coverage-note";

export type { CoverageNote };
export { resolveCoverageNotes };

function formatCoverageNote(
  note: CoverageNote,
  t: ReturnType<typeof useTranslations<"common">>,
): string {
  if (typeof note === "string") return note;
  if (note.code === "thin_evidence") {
    return t("noteThinEvidence", {
      thin_n: note.thin_n ?? 0,
      pct: note.pct ?? 0,
    });
  }
  if (note.code === "capped_sources") {
    return t("noteCappedSources", { sources: note.sources ?? "" });
  }
  return note.message ?? "";
}

/** Compact muted mono footnotes for DSS coverage_notes. */
export function CoverageNotesList({ notes }: { notes: CoverageNote[] }) {
  const t = useTranslations("common");
  if (!notes.length) return null;
  return (
    <aside className="space-y-1" aria-label={t("coverageNotes")}>
      <p
        className="text-[0.65rem] font-semibold uppercase tracking-[0.12em] text-[var(--muted)]"
      >
        {t("coverageNotes")}
      </p>
      <ul className="space-y-0.5">
        {notes.map((note) => {
          const text = formatCoverageNote(note, t);
          if (!text) return null;
          return (
            <li
              key={coverageNoteKey(note)}
              className="text-xs text-[var(--muted)]"
              style={{ fontFamily: "var(--mono)" }}
            >
              {text}
            </li>
          );
        })}
      </ul>
    </aside>
  );
}
