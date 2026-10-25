"use client";

import { FormEvent, useState, useTransition } from "react";
import { useTranslations } from "next-intl";

type TaxItem = {
  title?: string;
  uri?: string;
  code?: string;
  class_name?: string;
};

type TaxResponse = {
  items?: TaxItem[];
  total?: number;
  disclaimer?: string;
  error?: string;
  provider?: string;
};

type Provider = "esco" | "jobtech";

export function TaxonomySearchPanel() {
  const t = useTranslations("taxonomy");
  const [provider, setProvider] = useState<Provider>("esco");
  const [q, setQ] = useState(() => t("defaultQueryEsco"));
  const [type, setType] = useState<"occupation" | "skill">("occupation");
  const [data, setData] = useState<TaxResponse | null>(null);
  const [error, setError] = useState("");
  const [pending, startTransition] = useTransition();

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    const query = q.trim();
    if (!query) return;
    startTransition(async () => {
      setError("");
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
        const params = new URLSearchParams({ q: query, type, limit: "8" });
        if (provider === "esco") params.set("language", "en");
        const path =
          provider === "esco" ? "/api/v1/taxonomy/esco/search" : "/api/v1/taxonomy/jobtech/search";
        const res = await fetch(`${apiUrl}${path}?${params}`);
        const body = (await res.json()) as TaxResponse;
        if (!res.ok) throw new Error(body.error || res.statusText);
        setData(body);
      } catch (err) {
        setData(null);
        setError(err instanceof Error ? err.message : t("searchFailed"));
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
          <span className="opacity-60">{t("provider")}</span>
          <select
            value={provider}
            onChange={(e) => {
              const next = e.target.value as Provider;
              setProvider(next);
              if (next === "jobtech" && type === "occupation") {
                setQ(t("defaultQueryJobtech"));
              }
              if (next === "esco") setQ(t("defaultQueryEsco"));
            }}
            className="rounded border border-[var(--line)] bg-transparent px-2 py-1.5 text-sm"
          >
            <option value="esco">ESCO (EU)</option>
            <option value="jobtech">JobTech (SE)</option>
          </select>
        </label>
        <label className="flex min-w-[12rem] flex-1 flex-col gap-1 text-xs">
          <span className="opacity-60">{t("query")}</span>
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            className="rounded border border-[var(--line)] bg-transparent px-2 py-1.5 text-sm"
            placeholder={
              provider === "jobtech" ? t("placeholderJobtech") : t("placeholderEsco")
            }
            autoComplete="off"
          />
        </label>
        <label className="flex flex-col gap-1 text-xs">
          <span className="opacity-60">{t("type")}</span>
          <select
            value={type}
            onChange={(e) => setType(e.target.value as "occupation" | "skill")}
            className="rounded border border-[var(--line)] bg-transparent px-2 py-1.5 text-sm"
          >
            <option value="occupation">{t("occupation")}</option>
            <option value="skill">{t("skill")}</option>
          </select>
        </label>
        <button
          type="submit"
          disabled={pending}
          className="rounded bg-slate-800 px-3 py-2 text-sm text-white disabled:opacity-50"
        >
          {pending ? t("searching") : t("search")}
        </button>
      </form>
      {error ? <p className="mt-2 text-sm text-red-700">{error}</p> : null}
      {data?.disclaimer ? <p className="mt-2 text-xs opacity-60">{data.disclaimer}</p> : null}
      {items.length > 0 ? (
        <ul className="mt-3 space-y-2 text-sm">
          {items.map((item) => (
            <li key={item.uri || item.code || item.title} className="border-b border-[var(--line)] py-2">
              <div className="font-medium">{item.title}</div>
              <div className="text-xs opacity-60">
                {item.code ? t("conceptId", { code: item.code }) : null}
                {item.code && item.class_name ? " · " : null}
                {item.class_name || null}
              </div>
              {item.uri ? (
                <a
                  href={item.uri}
                  target="_blank"
                  rel="noreferrer"
                  className="text-xs text-teal-800 underline"
                >
                  {t("openConcept")}
                </a>
              ) : null}
            </li>
          ))}
        </ul>
      ) : data && !error ? (
        <p className="mt-3 text-sm opacity-60">{t("noMatches")}</p>
      ) : null}
      {typeof data?.total === "number" ? (
        <p className="mt-2 text-xs opacity-50">
          {t("hits", { provider: data.provider || provider, total: data.total })}
        </p>
      ) : null}
    </section>
  );
}

/** @deprecated Use TaxonomySearchPanel */
export function EscoSearchPanel() {
  return <TaxonomySearchPanel />;
}
