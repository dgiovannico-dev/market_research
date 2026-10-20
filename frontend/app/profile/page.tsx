async function getJSON(path: string) {
  const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  const res = await fetch(`${API_URL}${path}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`${path} failed`);
  return res.json();
}

export default async function ProfilePage() {
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
    error = e instanceof Error ? e.message : "Failed";
  }

  const gapItems = (gaps.gaps as Array<Record<string, unknown>>) || [];
  const recItems = (recs.items as Array<Record<string, unknown>>) || [];

  return (
    <div className="space-y-4">
      <section className="card p-4">
        <h2 className="text-lg font-semibold">Profile & Skills</h2>
        {error && <p className="text-sm text-red-700">{error}</p>}
        <p className="text-sm">
          {String(profile.display_name)} · {String(profile.residence_country)} · target{" "}
          {String(profile.target_rate_amount)} {String(profile.rate_currency)}/{String(profile.rate_unit)}
        </p>
        <p className="mt-2 text-xs opacity-70">{String(gaps.disclaimer || "")}</p>
        <p className="mt-1 text-sm">Owned: {((gaps.owned_skills as string[]) || []).join(", ")}</p>
      </section>

      <section className="card p-4">
        <h3 className="font-semibold">Priority skill gaps (observed demand)</h3>
        <ul className="mt-3 space-y-2 text-sm">
          {gapItems.slice(0, 15).map((g) => (
            <li key={String(g.technology)} className="flex justify-between border-b border-[var(--line)] py-1">
              <span>
                {String(g.technology)} <span className="text-xs opacity-60">({String(g.gap_type)})</span>
              </span>
              <span>score {String(g.priority_score)}</span>
            </li>
          ))}
        </ul>
      </section>

      <section className="card p-4">
        <h3 className="font-semibold">Compatible opportunities (heuristic match)</h3>
        <ul className="mt-3 space-y-2 text-sm">
          {recItems.map((r) => (
            <li key={String(r.job_id)} className="border-b border-[var(--line)] py-2">
              <div className="font-medium">{String(r.title)}</div>
              <div className="text-xs opacity-70">
                match {String(r.skill_match)} · {String(r.country_code)} · {String(r.contract_type)}/
                {String(r.remote_type)}
              </div>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
