"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";

type SourceRow = {
  id: number;
  name?: string;
  connector_type?: string;
  is_credentialed_scaffold?: boolean;
};

export function RunFreeSourcesButton({ sources }: { sources: SourceRow[] }) {
  const t = useTranslations("sources");
  const free = sources.filter((s) => !s.is_credentialed_scaffold);
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(false);

  async function runAll() {
    if (!free.length) {
      setStatus(t("runFreeEmpty"));
      return;
    }
    setLoading(true);
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    let ok = 0;
    let failed = 0;
    let inserted = 0;
    for (const s of free) {
      setStatus(
        t("runFreeProgress", {
          name: s.name || s.connector_type || s.id,
          current: ok + failed + 1,
          total: free.length,
        }),
      );
      try {
        const res = await fetch(`${apiUrl}/api/v1/sources/${s.id}/run`, {
          method: "POST",
        });
        const data = await res.json().catch(() => ({}));
        if (!res.ok) {
          failed += 1;
          continue;
        }
        ok += 1;
        inserted += Number(data.inserted || 0);
      } catch {
        failed += 1;
      }
    }
    setStatus(t("runFreeDone", { ok, failed, inserted }));
    setLoading(false);
  }

  return (
    <div className="mt-3">
      <button
        type="button"
        onClick={() => void runAll()}
        disabled={loading || free.length === 0}
        aria-busy={loading}
        className="rounded bg-slate-800 px-3 py-2 text-sm font-medium text-white disabled:opacity-50"
      >
        {loading ? t("runFreeWorking") : t("runFreeAction", { count: free.length })}
      </button>
      {status ? <p className="mt-2 text-xs opacity-70">{status}</p> : null}
    </div>
  );
}
