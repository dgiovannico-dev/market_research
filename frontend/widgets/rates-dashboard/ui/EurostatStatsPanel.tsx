"use client";

import { FormEvent, useState, useTransition } from "react";
import { useTranslations } from "next-intl";

type SeriesItem = { index?: string; value?: number | string };
type SeriesResponse = {
  label?: string;
  items?: SeriesItem[];
  total_values?: number;
  disclaimer?: string;
  error?: string;
  dataset?: string;
  geo?: string;
};

export function EurostatStatsPanel() {
  const t = useTranslations("eurostat");
  const [geo, setGeo] = useState("DE");
  const [dataset, setDataset] = useState<"earn_ses_hourly" | "une_rt_a">("earn_ses_hourly");
  const [data, setData] = useState<SeriesResponse | null>(null);
  const [error, setError] = useState("");
  const [pending, startTransition] = useTransition();

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    startTransition(async () => {
      setError("");
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
        const params = new URLSearchParams({
          dataset,
          geo: geo.trim().toUpperCase() || "DE",
          limit: "8",
        });
        if (dataset === "earn_ses_hourly") params.set("time", "2022");
        const res = await fetch(`${apiUrl}/api/v1/stats/eurostat/series?${params}`);
        const body = (await res.json()) as SeriesResponse;
        if (!res.ok) throw new Error(body.error || res.statusText);
        setData(body);
      } catch (err) {
        setData(null);
        setError(err instanceof Error ? err.message : t("lookupFailed"));
      }
    });
  }

  const items = data?.items ?? [];

  return (
    <section className="card p-4">
      <h3 className="font-semibold">{t("title")}</h3>
      <p className="mt-1 text-sm opacity-70">{t("subtitle")}</p>
      <form onSubmit={onSubmit} className="mt-3 flex flex-wrap items-end gap-2">
        <label className="flex flex-col gap-1 text-xs">
          <span className="opacity-60">{t("dataset")}</span>
          <select
            value={dataset}
            onChange={(e) => setDataset(e.target.value as "earn_ses_hourly" | "une_rt_a")}
            className="rounded border border-[var(--line)] bg-transparent px-2 py-1.5 text-sm"
          >
            <option value="earn_ses_hourly">{t("earnSes")}</option>
            <option value="une_rt_a">{t("uneRt")}</option>
          </select>
        </label>
        <label className="flex flex-col gap-1 text-xs">
          <span className="opacity-60">{t("country")}</span>
          <input
            value={geo}
            onChange={(e) => setGeo(e.target.value)}
            className="w-20 rounded border border-[var(--line)] bg-transparent px-2 py-1.5 text-sm uppercase"
            maxLength={8}
            autoComplete="off"
          />
        </label>
        <button
          type="submit"
          disabled={pending}
          className="rounded bg-slate-800 px-3 py-2 text-sm text-white disabled:opacity-50"
        >
          {pending ? t("loading") : t("loadSeries")}
        </button>
      </form>
      {error ? <p className="mt-2 text-sm text-red-700">{error}</p> : null}
      {data?.disclaimer ? <p className="mt-2 text-xs opacity-60">{data.disclaimer}</p> : null}
      {data?.label ? <p className="mt-2 text-sm font-medium">{data.label}</p> : null}
      {items.length > 0 ? (
        <ul className="mt-2 space-y-1 text-sm">
          {items.map((row) => (
            <li key={String(row.index)} className="flex justify-between gap-4 border-b border-[var(--line)] py-1">
              <span className="opacity-60">{t("idx", { index: String(row.index) })}</span>
              <span>{row.value == null ? "—" : String(row.value)}</span>
            </li>
          ))}
        </ul>
      ) : null}
      {typeof data?.total_values === "number" ? (
        <p className="mt-2 text-xs opacity-50">
          {t("footer", {
            dataset: String(data.dataset),
            geo: String(data.geo),
            total: data.total_values,
          })}
        </p>
      ) : null}
    </section>
  );
}
