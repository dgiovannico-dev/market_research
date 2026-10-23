"use client";

import { useState, type FormEvent } from "react";
import { useTranslations } from "next-intl";
import { parseCountryCodes } from "@/features/country-filter";

type Props = {
  busy?: boolean;
  onCreate: (fields: {
    name: string;
    query_text: string;
    countries?: string[];
  }) => Promise<boolean>;
};

export function CreateFocusForm({ busy, onCreate }: Props) {
  const t = useTranslations("research");
  const [name, setName] = useState("");
  const [queryText, setQueryText] = useState("");
  const [countriesRaw, setCountriesRaw] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault();
    const n = name.trim();
    const q = queryText.trim();
    if (!n || !q) return;
    setSubmitting(true);
    try {
      const countries = parseCountryCodes(countriesRaw);
      const ok = await onCreate({
        name: n,
        query_text: q,
        ...(countries.length ? { countries } : {}),
      });
      if (ok) {
        setName("");
        setQueryText("");
        setCountriesRaw("");
      }
    } finally {
      setSubmitting(false);
    }
  };

  const blocked = busy || submitting;

  return (
    <form className="card space-y-3 p-5" onSubmit={(e) => void onSubmit(e)}>
      <div>
        <h2 className="font-display text-lg font-semibold tracking-tight text-[var(--ink)]">
          {t("createFocusTitle")}
        </h2>
        <p className="mt-1 text-sm text-[var(--muted)]">{t("createFocusHint")}</p>
      </div>
      <label className="block text-xs text-[var(--muted)]">
        {t("labelField")}
        <input
          className="mt-1 w-full rounded border border-[var(--line)] bg-transparent px-3 py-2 text-sm text-[var(--ink)]"
          value={name}
          disabled={blocked}
          onChange={(e) => setName(e.target.value)}
          autoComplete="off"
        />
      </label>
      <label className="block text-xs text-[var(--muted)]">
        {t("queryField")}
        <textarea
          className="mt-1 min-h-20 w-full rounded border border-[var(--line)] bg-transparent px-3 py-2 text-sm text-[var(--ink)]"
          style={{ fontFamily: "var(--mono)" }}
          value={queryText}
          disabled={blocked}
          onChange={(e) => setQueryText(e.target.value)}
          placeholder={t("queryPlaceholder")}
        />
      </label>
      <label className="block text-xs text-[var(--muted)]">
        {t("countriesField")}
        <input
          className="mt-1 w-full rounded border border-[var(--line)] bg-transparent px-3 py-2 text-sm text-[var(--ink)]"
          style={{ fontFamily: "var(--mono)" }}
          value={countriesRaw}
          disabled={blocked}
          onChange={(e) => setCountriesRaw(e.target.value)}
          placeholder={t("countriesPlaceholder")}
          autoComplete="off"
        />
      </label>
      <p className="text-[0.7rem] text-[var(--muted)]">{t("countriesHint")}</p>
      <button
        type="submit"
        disabled={blocked || !name.trim() || !queryText.trim()}
        className="rounded-full bg-[var(--signal)] px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
      >
        {submitting ? t("creating") : t("createFocus")}
      </button>
    </form>
  );
}
