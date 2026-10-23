import { getTranslations } from "next-intl/server";
import { EvaluateAlertsButton } from "@/features/ops-llm";
import { getJSON } from "@/shared/api";
import { formatDateMinute } from "@/shared/lib/formatDateTime";

async function fetchAlerts() {
  return getJSON<{ items?: Record<string, unknown>[] }>("/api/v1/alerts");
}

export default async function AlertsPage() {
  const t = await getTranslations("alerts");
  let data: { items?: Record<string, unknown>[] } = { items: [] };
  let error: string | null = null;
  try {
    data = await fetchAlerts();
  } catch (e) {
    error = e instanceof Error ? e.message : t("loadFailed");
  }

  const items = data.items || [];

  return (
    <div className="space-y-5">
      <header className="flex flex-wrap items-end justify-between gap-3">
        <div className="space-y-1">
          <h2 className="font-display text-2xl font-semibold tracking-tight text-[var(--ink)]">
            {t("title")}
          </h2>
          <p className="max-w-2xl text-sm text-[var(--muted)]">{t("subtitle")}</p>
        </div>
        <EvaluateAlertsButton />
      </header>

      {error ? (
        <div
          className="rounded-xl border border-[var(--warn)]/40 bg-[var(--card)] p-4 text-sm text-[var(--warn)]"
          role="alert"
        >
          {error}
        </div>
      ) : null}

      {items.length === 0 && !error ? (
        <div className="rounded-xl border border-[var(--line)] bg-[var(--card)] p-6 text-sm text-[var(--muted)]">
          {t("empty")}
        </div>
      ) : null}

      {items.map((a) => (
        <article
          key={String(a.id)}
          className="rounded-xl border border-[var(--line)] bg-[var(--card)] p-4 text-sm"
        >
          <h3 className="font-display text-base font-semibold tracking-tight text-[var(--ink)]">
            {String(a.name)}
          </h3>
          <p className="text-xs text-[var(--muted)]" style={{ fontFamily: "var(--mono)" }}>
            {String(a.rule_type)}
          </p>
          <p className="mt-2 text-[var(--ink)]">
            {t("lastTriggered", {
              when: formatDateMinute(
                typeof a.last_triggered_at === "string" ? a.last_triggered_at : null,
                t("never"),
              ),
            })}
          </p>
          <p className="mt-1 text-xs text-[var(--muted)]">
            {t("evidence", { text: String(a.last_evidence ?? "—") })}
          </p>
        </article>
      ))}
    </div>
  );
}
