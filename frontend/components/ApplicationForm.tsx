"use client";

import { useState } from "react";

export function ApplicationForm() {
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
    setStatus(res.ok ? "Saved" : `Error ${res.status}`);
    if (res.ok) window.location.reload();
  }

  return (
    <form onSubmit={onSubmit} className="card grid gap-2 p-4 md:grid-cols-3">
      <input name="applied_at" type="date" required className="rounded border px-3 py-2" />
      <input name="job_id" type="number" placeholder="Job id (optional)" className="rounded border px-3 py-2" />
      <input name="channel" placeholder="Channel" className="rounded border px-3 py-2" />
      <input name="requested_rate" type="number" placeholder="Requested rate" className="rounded border px-3 py-2" />
      <input name="response" placeholder="Response" className="rounded border px-3 py-2" />
      <input name="outcome" placeholder="Outcome" className="rounded border px-3 py-2" />
      <label className="flex items-center gap-2 text-sm">
        <input name="interview" type="checkbox" /> Interview
      </label>
      <button className="rounded bg-teal-700 px-3 py-2 text-white md:col-span-2">Add application</button>
      {status && <p className="text-xs opacity-70 md:col-span-3">{status}</p>}
    </form>
  );
}
