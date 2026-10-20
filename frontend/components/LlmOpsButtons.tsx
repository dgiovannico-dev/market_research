"use client";

import { useState } from "react";

export function LlmOpsButtons() {
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState<"classify" | "eval" | null>(null);
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  async function post(path: string, kind: "classify" | "eval") {
    setLoading(kind);
    setStatus("Running…");
    try {
      const res = await fetch(`${apiUrl}${path}`, { method: "POST" });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || res.statusText);
      setStatus(JSON.stringify(data, null, 0).slice(0, 400));
    } catch (e) {
      setStatus(e instanceof Error ? e.message : "Failed");
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
          {loading === "classify" ? "Classifying…" : "Run LLM classify (batch)"}
        </button>
        <button
          type="button"
          disabled={loading !== null}
          onClick={() => post("/api/v1/llm/evaluation/run?limit=50", "eval")}
          className="rounded border border-[var(--line)] px-3 py-2 text-sm hover:border-teal-600 disabled:opacity-50"
        >
          {loading === "eval" ? "Evaluating…" : "Run rules consistency eval"}
        </button>
      </div>
      {status ? <pre className="overflow-x-auto text-xs opacity-70">{status}</pre> : null}
    </div>
  );
}
