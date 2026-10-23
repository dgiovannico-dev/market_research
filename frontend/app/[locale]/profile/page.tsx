import { getTranslations } from "next-intl/server";
import { getJSON } from "@/shared/api";

function str(value: unknown, fallback = "—"): string {
  if (value == null || value === "") return fallback;
  return String(value);
}

export default async function ProfilePage() {
  const t = await getTranslations("profile");
  let profile: Record<string, unknown> = {};
  let gaps: Record<string, unknown> = {};
  let recs: Record<string, unknown> = {};
  let error: string | null = null;
  try {
    [profile, gaps, recs] = await Promise.all([
      getJSON("/api/v1/profile"),
      getJSON("/api/v1/profile/skill-gaps"),
      getJSON("/api/v1/profile/recommendations"),
    ]);
  } catch (e) {
    error = e instanceof Error ? e.message : t("loadFailed");
  }

  const gapItems = (gaps.gaps as Array<Record<string, unknown>>) || [];
  const recItems = (recs.items as Array<Record<string, unknown>>) || [];
  const owned = ((gaps.owned_skills as string[]) || []).join(", ");
  const hasProfile = Boolean(profile.display_name);

  const summary = hasProfile
    ? [
        str(profile.display_name),
        str(profile.residence_country),
        t("targetLine", {
          amount: str(profile.target_rate_amount),
          currency: str(profile.rate_currency),
          unit: str(profile.rate_unit),
        }),
      ].join(" · ")
    : null;

  return (
    <div className="space-y-5">
      <header className="space-y-1">
        <h2 className="font-display text-2xl font-semibold tracking-tight text-[var(--ink)]">
          {t("title")}
        </h2>
        {error ? (
          <p className="text-sm text-[var(--warn)]" role="alert">
            {error}
          </p>
        ) : null}
        {summary ? (
          <p className="text-sm text-[var(--ink)]">{summary}</p>
        ) : !error ? (
          <p className="text-sm text-[var(--muted)]">{t("noProfile")}</p>
        ) : null}
        {gaps.disclaimer ? (
          <p className="text-xs text-[var(--muted)]">{str(gaps.disclaimer)}</p>
        ) : null}
        <p className="text-sm text-[var(--muted)]">
          {t("owned", { list: owned || "—" })}
        </p>
      </header>

      <section className="rounded-xl border border-[var(--line)] bg-[var(--card)] p-4">
        <h3 className="font-display text-base font-semibold tracking-tight text-[var(--ink)]">
          {t("gapsTitle")}
        </h3>
        {gapItems.length === 0 ? (
          <p className="mt-3 text-sm text-[var(--muted)]">{t("gapsEmpty")}</p>
        ) : (
          <ul className="mt-3 space-y-2 text-sm">
            {gapItems.slice(0, 15).map((g) => (
              <li
                key={str(g.technology)}
                className="flex justify-between border-b border-[var(--line)] py-1.5 last:border-b-0"
              >
                <span className="text-[var(--ink)]">
                  {str(g.technology)}{" "}
                  <span className="text-xs text-[var(--muted)]">
                    ({str(g.gap_type)})
                  </span>
                </span>
                <span
                  className="text-[var(--muted)]"
                  style={{ fontFamily: "var(--mono)" }}
                >
                  {t("score", { value: str(g.priority_score) })}
                </span>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="rounded-xl border border-[var(--line)] bg-[var(--card)] p-4">
        <h3 className="font-display text-base font-semibold tracking-tight text-[var(--ink)]">
          {t("recsTitle")}
        </h3>
        {recItems.length === 0 ? (
          <p className="mt-3 text-sm text-[var(--muted)]">{t("recsEmpty")}</p>
        ) : (
          <ul className="mt-3 space-y-2 text-sm">
            {recItems.map((r) => (
              <li
                key={str(r.job_id)}
                className="border-b border-[var(--line)] py-2 last:border-b-0"
              >
                <div className="font-medium text-[var(--ink)]">{str(r.title)}</div>
                <div className="text-xs text-[var(--muted)]">
                  {t("matchLine", {
                    score: str(r.skill_match),
                    country: str(r.country_code),
                    contract: str(r.contract_type),
                    remote: str(r.remote_type),
                  })}
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
