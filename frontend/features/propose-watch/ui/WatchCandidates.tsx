"use client";

import { useTranslations } from "next-intl";
import { useState } from "react";
import { api, type ProposedWatchCandidate } from "@/lib/api";

type Props = {
  candidates: ProposedWatchCandidate[];
};

export function WatchCandidates({ candidates }: Props) {
  const t = useTranslations("assistant");
  const [busyKey, setBusyKey] = useState<string | null>(null);
  const [accepted, setAccepted] = useState<Record<string, string>>({});
  const [error, setError] = useState<string | null>(null);

  if (candidates.length === 0) {
    return <p className="text-sm text-[var(--muted)]">{t("noCandidates")}</p>;
  }

  const accept = async (candidate: ProposedWatchCandidate) => {
    const key = `${candidate.kind}:${candidate.query_text}`;
    setBusyKey(key);
    setError(null);
    try {
      const saved = await api.acceptResearchWatch({
        name: candidate.name,
        query_text: candidate.query_text,
        kind: candidate.kind,
      });
      setAccepted((prev) => ({ ...prev, [key]: saved.name }));
    } catch (e) {
      setError(e instanceof Error ? e.message : t("acceptFailed"));
    } finally {
      setBusyKey(null);
    }
  };

  return (
    <div className="space-y-3">
      <h4 className="font-display text-sm font-semibold tracking-tight text-[var(--ink)]">
        {t("proposedWatches")}
      </h4>
      {error ? <p className="text-sm text-[var(--warn)]">{error}</p> : null}
      <ul className="space-y-2">
        {candidates.map((candidate) => {
          const key = `${candidate.kind}:${candidate.query_text}`;
          const savedName = accepted[key];
          return (
            <li
              key={key}
              className="flex flex-wrap items-start justify-between gap-2 rounded-md border border-[var(--line)] px-3 py-2"
            >
              <div className="min-w-0 flex-1 space-y-0.5">
                <p className="text-sm font-medium text-[var(--ink)]">{candidate.name}</p>
                <p className="font-mono text-xs text-[var(--muted)]">
                  {candidate.kind} · {candidate.query_text}
                  {typeof candidate.support === "number"
                    ? ` · support=${candidate.support}`
                    : null}
                </p>
                {candidate.rationale ? (
                  <p className="text-xs text-[var(--muted)]">{candidate.rationale}</p>
                ) : null}
                {savedName ? (
                  <p className="text-xs signal-text">
                    {t("accepted", { name: savedName })}
                  </p>
                ) : null}
              </div>
              <button
                type="button"
                disabled={busyKey === key || Boolean(savedName)}
                className="rounded-full bg-[var(--signal)] px-3 py-1.5 text-xs font-medium text-white transition-opacity hover:opacity-90 disabled:opacity-50"
                onClick={() => void accept(candidate)}
              >
                {busyKey === key
                  ? t("accepting")
                  : savedName
                    ? t("acceptedShort")
                    : t("acceptWatch")}
              </button>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
