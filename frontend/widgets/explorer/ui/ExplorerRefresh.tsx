"use client";

import { startTransition, useState } from "react";
import { useTranslations } from "next-intl";
import { Link, useRouter } from "@/i18n/navigation";
import { api } from "@/lib/api";
import type { ResearchIntent } from "@/entities/research-intent";

type Props = {
  intents: ResearchIntent[];
  /** Prefill from Explore `query_id` filter when set. */
  preferredIntentId?: number | null;
};

/** Secondary ops control — Explore itself is DB-first. */
export function ExplorerRefresh({ intents, preferredIntentId }: Props) {
  const t = useTranslations("explorer");
  const router = useRouter();
  const initial =
    preferredIntentId && intents.some((i) => i.id === preferredIntentId)
      ? preferredIntentId
      : (intents.find((i) => i.enabled)?.id ?? "");
  const [intentId, setIntentId] = useState<number | "">(initial);
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  if (!intents.length) {
    return (
      <p className="text-sm text-[var(--muted)]">
        {t("refreshNeedsIntent")}{" "}
        <Link href="/focus" className="underline signal-text">
          {t("openFocus")}
        </Link>
      </p>
    );
  }

  async function run() {
    if (intentId === "") return;
    setBusy(true);
    setMsg(null);
    setError(null);
    try {
      await api.syncResearchIntent(intentId);
      setMsg(t("refreshOk"));
      startTransition(() => {
        router.refresh();
      });
    } catch (e) {
      setError(e instanceof Error ? e.message : t("refreshFailed"));
    } finally {
      setBusy(false);
    }
  }

  return (
    <aside className="space-y-2 rounded border border-dashed border-[var(--line)] p-3">
      <p className="font-display text-xs uppercase tracking-[0.2em] text-[var(--muted)]">
        {t("refreshEyebrow")}
      </p>
      <p className="text-xs text-[var(--muted)]">{t("refreshHint")}</p>
      <div className="flex flex-wrap gap-2">
        <select
          className="rounded border border-[var(--line)] bg-transparent px-2 py-1.5 text-sm"
          value={intentId === "" ? "" : String(intentId)}
          onChange={(e) =>
            setIntentId(e.target.value ? Number.parseInt(e.target.value, 10) : "")
          }
        >
          {intents.map((it) => (
            <option key={it.id} value={it.id}>
              [{it.kind}] {it.name}
            </option>
          ))}
        </select>
        <button
          type="button"
          disabled={busy || intentId === ""}
          className="rounded border border-[var(--line)] px-3 py-1.5 text-sm hover:border-[var(--signal)] disabled:opacity-50"
          onClick={() => void run()}
        >
          {busy ? t("refreshing") : t("refreshFromSources")}
        </button>
      </div>
      {msg ? <p className="text-sm signal-text">{msg}</p> : null}
      {error ? <p className="text-sm text-[var(--warn)]">{error}</p> : null}
    </aside>
  );
}
