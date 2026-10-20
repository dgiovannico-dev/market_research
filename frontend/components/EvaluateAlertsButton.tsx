"use client";

import { useState } from "react";

export function EvaluateAlertsButton() {
  const [msg, setMsg] = useState("");
  async function run() {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    const res = await fetch(`${apiUrl}/api/v1/alerts/evaluate`, { method: "POST" });
    const data = await res.json();
    setMsg(res.ok ? `Fired: ${data.fired?.length ?? 0}` : "Error");
    if (res.ok) window.location.reload();
  }
  return (
    <div>
      <button onClick={run} className="rounded bg-teal-700 px-3 py-2 text-sm text-white">
        Evaluate now
      </button>
      {msg && <p className="mt-1 text-xs opacity-70">{msg}</p>}
    </div>
  );
}
