import { getTranslations } from "next-intl/server";
import { ApplicationForm } from "@/widgets/applications";
import {
  ApplicationsTable,
  type ApplicationRow,
} from "@/widgets/applications";
import { getJSON } from "@/shared/api";

async function fetchApps() {
  return getJSON<{
    items?: Record<string, unknown>[];
    summary?: Record<string, unknown>;
  }>("/api/v1/applications");
}

export default async function ApplicationsPage() {
  const t = await getTranslations("applications");
  let data: { items?: Record<string, unknown>[]; summary?: Record<string, unknown> } = {};
  let error: string | null = null;
  try {
    data = await fetchApps();
  } catch (e) {
    error = e instanceof Error ? e.message : t("loadFailed");
  }
  const metrics = (data.summary?.metrics || {}) as Record<string, unknown>;
  const items = data.items || [];

  return (
    <div className="space-y-5">
      <header className="space-y-1">
        <h2 className="font-display text-2xl font-semibold tracking-tight text-[var(--ink)]">
          {t("title")}
        </h2>
        <p className="max-w-2xl text-sm text-[var(--muted)]">{t("subtitle")}</p>
      </header>

      {error ? (
        <div
          className="rounded-xl border border-[var(--warn)]/40 bg-[var(--card)] p-4 text-sm text-[var(--warn)]"
          role="alert"
        >
          {error}
        </div>
      ) : null}

      <section className="rounded-xl border border-[var(--line)] bg-[var(--card)] p-4">
        <h3 className="font-display text-base font-semibold tracking-tight text-[var(--ink)]">
          {t("pipelineTitle")}
        </h3>
        <div className="mt-3 grid gap-2 text-sm md:grid-cols-4">
          <div className="rounded-lg border border-[var(--line)] px-3 py-2.5 text-[var(--ink)]">
            {t("metricApps")}:{" "}
            <span style={{ fontFamily: "var(--mono)" }}>
              {String(data.summary?.applications ?? 0)}
            </span>
          </div>
          <div className="rounded-lg border border-[var(--line)] px-3 py-2.5 text-[var(--ink)]">
            {t("metricResponse")}:{" "}
            <span style={{ fontFamily: "var(--mono)" }}>
              {String(metrics.response_rate ?? "—")}
            </span>
          </div>
          <div className="rounded-lg border border-[var(--line)] px-3 py-2.5 text-[var(--ink)]">
            {t("metricInterview")}:{" "}
            <span style={{ fontFamily: "var(--mono)" }}>
              {String(metrics.interview_rate ?? "—")}
            </span>
          </div>
          <div className="rounded-lg border border-[var(--line)] px-3 py-2.5 text-[var(--ink)]">
            {t("metricOffer")}:{" "}
            <span style={{ fontFamily: "var(--mono)" }}>
              {String(metrics.offer_rate ?? "—")}
            </span>
          </div>
        </div>
      </section>

      <ApplicationForm />

      <section className="overflow-x-auto rounded-xl border border-[var(--line)] bg-[var(--card)]">
        {!error ? (
          <ApplicationsTable
            items={items.map((row): ApplicationRow => ({
              id: (row.id as string | number) ?? Math.random(),
              applied_at:
                typeof row.applied_at === "string" ? row.applied_at : null,
              job_id: (row.job_id as string | number | null) ?? null,
              channel: typeof row.channel === "string" ? row.channel : null,
              response: typeof row.response === "string" ? row.response : null,
              outcome: typeof row.outcome === "string" ? row.outcome : null,
            }))}
          />
        ) : null}
      </section>
    </div>
  );
}
