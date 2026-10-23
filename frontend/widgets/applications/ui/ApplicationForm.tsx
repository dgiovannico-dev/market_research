"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";

const fieldClass =
  "rounded border border-[var(--line)] bg-transparent px-3 py-2 text-sm text-[var(--ink)] placeholder:text-[var(--muted)]";

export function ApplicationForm() {
  const t = useTranslations("applications");
  const [status, setStatus] = useState("");
  async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    const body = {
      applied_at: String(fd.get("applied_at")),
      job_id: fd.get("job_id") ? Number(fd.get("job_id")) : null,
      channel: String(fd.get("channel") || "") || null,
      requested_rate: fd.get("requested_rate") ? Number(fd.get("requested_rate")) : null,
      response: String(fd.get("response") || "") || null,
      interview: fd.get("interview") === "on",
      outcome: String(fd.get("outcome") || "") || null,
      rate_unit: "day",
      currency: "EUR",
    };
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    const res = await fetch(`${apiUrl}/api/v1/applications`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    setStatus(res.ok ? t("saved") : t("errorStatus", { status: res.status }));
    if (res.ok) window.location.reload();
  }

  return (
    <form
      onSubmit={onSubmit}
      className="grid gap-2 rounded-xl border border-[var(--line)] bg-[var(--card)] p-4 md:grid-cols-3"
    >
      <h3 className="font-display text-base font-semibold tracking-tight text-[var(--ink)] md:col-span-3">
        {t("formTitle")}
      </h3>
      <input name="applied_at" type="date" required className={fieldClass} />
      <input
        name="job_id"
        type="number"
        placeholder={t("placeholderJobId")}
        className={fieldClass}
      />
      <input name="channel" placeholder={t("placeholderChannel")} className={fieldClass} />
      <input
        name="requested_rate"
        type="number"
        placeholder={t("placeholderRate")}
        className={fieldClass}
      />
      <input name="response" placeholder={t("placeholderResponse")} className={fieldClass} />
      <input name="outcome" placeholder={t("placeholderOutcome")} className={fieldClass} />
      <label className="flex items-center gap-2 text-sm text-[var(--ink)]">
        <input name="interview" type="checkbox" className="accent-[var(--signal)]" />{" "}
        {t("interview")}
      </label>
      <button
        type="submit"
        className="rounded bg-[var(--signal)] px-3 py-2 text-sm font-medium text-white hover:opacity-90 md:col-span-2"
      >
        {t("submit")}
      </button>
      {status ? (
        <p className="text-xs text-[var(--muted)] md:col-span-3">{status}</p>
      ) : null}
    </form>
  );
}
