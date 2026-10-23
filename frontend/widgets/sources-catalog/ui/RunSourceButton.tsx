"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { runSource } from "@/features/run-source";

export function RunSourceButton({ sourceId }: { sourceId: number }) {
  const t = useTranslations("sources");
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(false);

  async function run() {
    setLoading(true);
    setStatus(t("runWorking"));
    try {
      const data = await runSource(sourceId);
      setStatus(
        t("runOk", {
          received: data.records_received ?? 0,
          inserted: data.inserted ?? 0,
          updated: data.updated ?? 0,
          dup: data.duplicates ?? 0,
        }),
      );
    } catch (e) {
      setStatus(e instanceof Error ? e.message : t("runFailed"));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="text-right">
      <button
        type="button"
        onClick={() => void run()}
        disabled={loading}
        aria-busy={loading}
        className="rounded bg-teal-700 px-3 py-2 text-sm font-medium text-white disabled:opacity-50"
      >
        {loading ? t("runWorking") : t("runAction")}
      </button>
      {status ? <p className="mt-2 max-w-xs text-xs opacity-70">{status}</p> : null}
    </div>
  );
}
