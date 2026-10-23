import { getTranslations } from "next-intl/server";

export type ExplorerJob = {
  id: number;
  title: string;
  company: string | null;
  country_code: string;
  contract_type: string;
  remote_type: string;
  canonical_url: string;
};

type Props = {
  total: number;
  items: ExplorerJob[];
};

export async function ExplorerJobList({ total, items }: Props) {
  const t = await getTranslations("explorer");

  return (
    <section className="card p-4">
      <h3 className="font-semibold">{t("jobsFound", { count: total })}</h3>
      {items.length === 0 ? (
        <p className="mt-3 text-sm opacity-70">{t("empty")}</p>
      ) : (
        <ul className="mt-3 space-y-2 text-sm">
          {items.map((j) => (
            <li
              key={j.id}
              className="flex justify-between gap-4 border-b border-[var(--line)] py-2"
            >
              <div>
                <div className="font-medium">{j.title}</div>
                <div className="text-xs opacity-60">
                  {j.company} · {j.country_code} · {j.contract_type}/{j.remote_type}
                </div>
              </div>
              <a
                href={j.canonical_url}
                className="signal-text underline"
                target="_blank"
                rel="noreferrer"
              >
                {t("sourceLink")}
              </a>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
