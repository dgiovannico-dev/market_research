"use client";

import { useState } from "react";

export function RunSourceButton({ sourceId }: { sourceId: number }) {
  const [status, setStatus] = useState<string>("");
  const [loading, setLoading] = useState(false);

  async function run() {
    setLoading(true);
    setStatus("Running…");
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const res = await fetch(`${apiUrl}/api/v1/sources/${sourceId}/run`, { method: "POST" });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || res.statusText);
      setStatus(
        `OK: received=${data.records_received} inserted=${data.inserted} updated=${data.updated} dup=${data.duplicates}`,
      );
    } catch (e) {
      setStatus(e instanceof Error ? e.message : "Failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="text-right">
      <button
        onClick={run}
        disabled={loading}
        className="rounded bg-teal-700 px-3 py-2 text-sm text-white disabled:opacity-50"
      >
        {loading ? "Collecting…" : "Run collection"}
      </button>
      {status && <p className="mt-2 max-w-xs text-xs opacity-70">{status}</p>}
    </div>
  );
}
