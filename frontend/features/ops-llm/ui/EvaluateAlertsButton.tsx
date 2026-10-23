"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";

export function EvaluateAlertsButton() {
  const t = useTranslations("alerts");
  const [msg, setMsg] = useState("");
  async function run() {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    const res = await fetch(`${apiUrl}/api/v1/alerts/evaluate`, { method: "POST" });
    const data = await res.json();
    setMsg(res.ok ? t("fired", { n: data.fired?.length ?? 0 }) : t("error"));
    if (res.ok) window.location.reload();
  }
  return (
    <div>
      <button
        onClick={run}
        className="rounded-lg border border-[var(--line)] bg-[var(--signal)] px-3 py-2 text-sm font-medium text-white"
      >
        {t("evaluate")}
      </button>
      {msg ? <p className="mt-1 text-xs text-[var(--muted)]">{msg}</p> : null}
    </div>
  );
}
