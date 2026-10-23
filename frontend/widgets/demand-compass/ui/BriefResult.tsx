"use client";

import { useTranslations } from "next-intl";
import { WatchCandidates } from "@/features/propose-watch";
import type { EvidenceBrief } from "@/lib/api";

type Props = {
  brief: EvidenceBrief;
};

function evidenceLine(item: Record<string, unknown>, index: number): string {
  const parts: string[] = [];
  if (typeof item.metric === "string") parts.push(item.metric);
  if (typeof item.source === "string") parts.push(`source=${item.source}`);
  for (const [key, value] of Object.entries(item)) {
    if (key === "metric" || key === "source") continue;
    if (typeof value === "number" || typeof value === "string" || typeof value === "boolean") {
      parts.push(`${key}=${String(value)}`);
    }
  }
  return parts.length > 0 ? parts.join(" · ") : `evidence[${index}]`;
}

export function BriefResult({ brief }: Props) {
  const t = useTranslations("assistant");
  const candidates = brief.proposed_intents ?? [];
  const showWatches =
    brief.brief_type === "suggest_watches" || candidates.length > 0;

  return (
    <section className="card space-y-4 p-5">
      <header className="flex flex-wrap items-baseline justify-between gap-2">
        <h3 className="font-display text-base font-semibold tracking-tight text-[var(--ink)]">
          {t("briefResultTitle")}
        </h3>
        <p className="font-mono text-xs text-[var(--muted)]">
          {brief.brief_type} · {brief.lens} · {t("sampleSize", { n: brief.sample_size })} ·{" "}
          {brief.status}
        </p>
      </header>

      <div className="space-y-1">
        <h4 className="font-display text-xs uppercase tracking-[0.14em] text-[var(--muted)]">
          {t("narrative")}
        </h4>
        <p className="whitespace-pre-wrap text-sm text-[var(--ink)]">{brief.narrative}</p>
      </div>

      {brief.evidence.length > 0 ? (
        <div className="space-y-1">
          <h4 className="font-display text-xs uppercase tracking-[0.14em] text-[var(--muted)]">
            {t("evidence")}
          </h4>
          <ul className="list-disc space-y-1 pl-5 font-mono text-xs text-[var(--muted)]">
            {brief.evidence.map((item, index) => (
              <li key={`${evidenceLine(item, index)}-${index}`}>
                {evidenceLine(item, index)}
              </li>
            ))}
          </ul>
        </div>
      ) : null}

      {brief.limits ? (
        <div className="space-y-1">
          <h4 className="font-display text-xs uppercase tracking-[0.14em] text-[var(--muted)]">
            {t("limits")}
          </h4>
          <p className="text-xs text-[var(--muted)]">{brief.limits}</p>
        </div>
      ) : null}

      {showWatches ? <WatchCandidates candidates={candidates} /> : null}
    </section>
  );
}
