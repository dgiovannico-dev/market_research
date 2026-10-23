"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";

type Kind = "classify" | "eval" | "gold";

export function LlmOpsButtons() {
  const t = useTranslations("llmOps");
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState<Kind | null>(null);
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  async function post(path: string, kind: Kind) {
    setLoading(kind);
    setStatus(t("running"));
    try {
      const res = await fetch(`${apiUrl}${path}`, { method: "POST" });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || res.statusText);
      setStatus(JSON.stringify(data, null, 0).slice(0, 500));
    } catch (e) {
      setStatus(e instanceof Error ? e.message : t("failed"));
    } finally {
      setLoading(null);
    }
  }

  return (
    <div className="mt-4 space-y-2">
      <div className="flex flex-wrap gap-2">
        <button
          type="button"
          disabled={loading !== null}
          onClick={() => post("/api/v1/llm/classification/run?limit=20", "classify")}
          className="rounded border border-[var(--line)] px-3 py-2 text-sm hover:border-teal-600 disabled:opacity-50"
        >
          {loading === "classify" ? t("classifying") : t("classify")}
        </button>
        <button
          type="button"
          disabled={loading !== null}
          onClick={() => post("/api/v1/llm/evaluation/run?limit=50", "eval")}
          className="rounded border border-[var(--line)] px-3 py-2 text-sm hover:border-teal-600 disabled:opacity-50"
        >
          {loading === "eval" ? t("evaluating") : t("eval")}
        </button>
        <button
          type="button"
          disabled={loading !== null}
          onClick={() => post("/api/v1/llm/evaluation/gold", "gold")}
          className="rounded border border-[var(--line)] px-3 py-2 text-sm hover:border-teal-600 disabled:opacity-50"
        >
          {loading === "gold" ? t("scoring") : t("gold")}
        </button>
      </div>
      {status ? <pre className="overflow-x-auto text-xs opacity-70">{status}</pre> : null}
    </div>
  );
}
