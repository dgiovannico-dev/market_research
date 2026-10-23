"use client";

import { startTransition } from "react";
import { useSearchParams } from "next/navigation";
import { useTranslations } from "next-intl";
import { usePathname, useRouter } from "@/i18n/navigation";
import { ScrollLoadFooter } from "@/shared/ui/ScrollLoadFooter";
import { SortableTh } from "@/shared/ui/SortableTh";
import { TableGuide } from "@/shared/ui/TableGuide";

export type JobRow = {
  id: number;
  title: string;
  company: string | null;
  source: string | null;
  country_code: string;
  contract_type: string;
  remote_type: string;
  published_at: string | null;
  canonical_url: string;
  /** DSS: thin = capped/snapshot source; omitted → treat as standard. */
  evidence_tier?: string | null;
  technologies: { name: string }[];
  rates: {
    amount_min: number | null;
    amount_max: number | null;
    currency: string | null;
    unit: string;
  }[];
};

const SORTABLE = [
  "published_at",
  "title",
  "company",
  "country_code",
  "contract_type",
  "source",
] as const;

type SortKey = (typeof SORTABLE)[number];

function formatRate(job: JobRow): string {
  const r = job.rates[0];
  if (!r) return "—";
  return `${r.amount_min ?? "?"}–${r.amount_max ?? "?"} ${r.currency ?? ""}/${r.unit}`;
}

function formatPublished(iso: string | null): string {
  if (!iso) return "—";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso.slice(0, 10);
  return d.toISOString().slice(0, 10);
}

type Props = {
  items: JobRow[];
  total: number;
  hasMore: boolean;
  loadingMore?: boolean;
  onLoadMore: () => void;
};

export function JobsTable({
  items,
  total,
  hasMore,
  loadingMore = false,
  onLoadMore,
}: Props) {
  const t = useTranslations("jobs");
  const searchParams = useSearchParams();
  const pathname = usePathname();
  const router = useRouter();

  const sort = (searchParams.get("sort") || "published_at") as SortKey | string;
  const order = (searchParams.get("order") || "desc") === "asc" ? "asc" : "desc";

  const setSort = (key: string) => {
    if (!(SORTABLE as readonly string[]).includes(key)) return;
    const params = new URLSearchParams(searchParams.toString());
    const nextOrder = sort === key && order === "desc" ? "asc" : "desc";
    if (key === "published_at" && nextOrder === "desc") {
      params.delete("sort");
      params.delete("order");
    } else {
      params.set("sort", key);
      params.set("order", nextOrder);
    }
    params.delete("page");
    const qs = params.toString();
    startTransition(() => {
      router.replace(qs ? `${pathname}?${qs}` : pathname, { scroll: false });
    });
  };

  return (
    <div className="space-y-3">
    <TableGuide
      represents={t("tableRepresents")}
      howToRead={t("tableHowToRead")}
    />
    <section className="overflow-hidden rounded-xl border border-[var(--line)] bg-[var(--card)]">
      <div className="overflow-x-auto">
        <table className="min-w-full text-left text-sm">
          <thead
            className="border-b border-[var(--line)] text-[0.65rem] font-semibold uppercase tracking-[0.12em] text-[var(--muted)]"
            style={{
              background: "color-mix(in srgb, var(--paper) 85%, var(--card))",
            }}
          >
            <tr>
              <SortableTh
                label={t("colPublished")}
                sortKey="published_at"
                activeSort={sort}
                order={order}
                onSort={setSort}
                ariaLabel={t("sortBy", { column: t("colPublished") })}
              />
              <SortableTh
                label={t("colTitle")}
                sortKey="title"
                activeSort={sort}
                order={order}
                onSort={setSort}
                ariaLabel={t("sortBy", { column: t("colTitle") })}
              />
              <SortableTh
                label={t("colCompany")}
                sortKey="company"
                activeSort={sort}
                order={order}
                onSort={setSort}
                ariaLabel={t("sortBy", { column: t("colCompany") })}
              />
              <SortableTh
                label={t("colSource")}
                sortKey="source"
                activeSort={sort}
                order={order}
                onSort={setSort}
                ariaLabel={t("sortBy", { column: t("colSource") })}
              />
              <SortableTh
                label={t("colCountry")}
                sortKey="country_code"
                activeSort={sort}
                order={order}
                onSort={setSort}
                ariaLabel={t("sortBy", { column: t("colCountry") })}
              />
              <SortableTh
                label={t("colContract")}
                sortKey="contract_type"
                activeSort={sort}
                order={order}
                onSort={setSort}
                ariaLabel={t("sortBy", { column: t("colContract") })}
              />
              <th className="px-3 py-2.5">{t("colRemote")}</th>
              <th className="px-3 py-2.5">{t("colTech")}</th>
              <th className="px-3 py-2.5">{t("colRate")}</th>
              <th className="px-3 py-2.5">{t("colUrl")}</th>
            </tr>
          </thead>
          <tbody>
            {items.map((job) => (
              <tr
                key={job.id}
                className="border-b border-[var(--line)] align-top last:border-b-0 hover:bg-[var(--paper)]/60"
              >
                <td
                  className="px-3 py-2.5 text-[var(--muted)]"
                  style={{ fontFamily: "var(--mono)" }}
                >
                  {formatPublished(job.published_at)}
                </td>
                <td className="px-3 py-2.5 font-medium text-[var(--ink)]">
                  <span className="inline-flex flex-wrap items-baseline gap-2">
                    {job.title}
                    {job.evidence_tier === "thin" ? (
                      <span
                        className="text-[0.65rem] font-normal uppercase tracking-wide text-[var(--muted)]"
                        style={{ fontFamily: "var(--mono)" }}
                        title={t("evidenceThinHint")}
                      >
                        {t("evidenceThin")}
                      </span>
                    ) : null}
                  </span>
                </td>
                <td className="px-3 py-2.5 text-xs text-[var(--muted)]">{job.company ?? "—"}</td>
                <td className="px-3 py-2.5 text-[var(--muted)]">{job.source}</td>
                <td
                  className="px-3 py-2.5 text-[var(--ink)]"
                  style={{ fontFamily: "var(--mono)" }}
                >
                  {job.country_code}
                </td>
                <td className="px-3 py-2.5 text-[var(--muted)]">{job.contract_type}</td>
                <td className="px-3 py-2.5 text-[var(--muted)]">{job.remote_type}</td>
                <td className="px-3 py-2.5 text-[var(--muted)]">
                  {job.technologies
                    .slice(0, 5)
                    .map((tech) => tech.name)
                    .join(", ")}
                </td>
                <td
                  className="px-3 py-2.5 text-[var(--ink)]"
                  style={{ fontFamily: "var(--mono)" }}
                >
                  {formatRate(job)}
                </td>
                <td className="px-3 py-2.5">
                  <a
                    className="font-medium underline signal-text"
                    href={job.canonical_url}
                    target="_blank"
                    rel="noreferrer"
                  >
                    {t("open")}
                  </a>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <ScrollLoadFooter
        hasMore={hasMore}
        loading={loadingMore}
        onLoadMore={onLoadMore}
        shown={items.length}
        total={total}
      />
    </section>
    </div>
  );
}

export function asJobRow(raw: Record<string, unknown>): JobRow | null {
  if (typeof raw.id !== "number" || typeof raw.title !== "string") return null;
  if (typeof raw.canonical_url !== "string") return null;
  const techs = Array.isArray(raw.technologies)
    ? raw.technologies.flatMap((t) => {
        if (!t || typeof t !== "object") return [];
        const name = (t as { name?: unknown }).name;
        return typeof name === "string" ? [{ name }] : [];
      })
    : [];
  const rates = Array.isArray(raw.rates)
    ? raw.rates.flatMap((r) => {
        if (!r || typeof r !== "object") return [];
        const row = r as Record<string, unknown>;
        return [
          {
            amount_min: typeof row.amount_min === "number" ? row.amount_min : null,
            amount_max: typeof row.amount_max === "number" ? row.amount_max : null,
            currency: typeof row.currency === "string" ? row.currency : null,
            unit: typeof row.unit === "string" ? row.unit : "",
          },
        ];
      })
    : [];
  return {
    id: raw.id,
    title: raw.title,
    company: typeof raw.company === "string" ? raw.company : null,
    source: typeof raw.source === "string" ? raw.source : null,
    country_code: typeof raw.country_code === "string" ? raw.country_code : "",
    contract_type: typeof raw.contract_type === "string" ? raw.contract_type : "",
    remote_type: typeof raw.remote_type === "string" ? raw.remote_type : "",
    published_at: typeof raw.published_at === "string" ? raw.published_at : null,
    canonical_url: raw.canonical_url,
    evidence_tier:
      typeof raw.evidence_tier === "string" ? raw.evidence_tier : undefined,
    technologies: techs,
    rates,
  };
}
