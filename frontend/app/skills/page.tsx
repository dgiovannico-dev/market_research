import { api } from "@/lib/api";

type Pair = {
  tech_a: string;
  tech_b: string;
  support: number;
  lift: number | null;
  jaccard: number | null;
  freq_a: number;
  freq_b: number;
  limits?: string;
};

export default async function SkillsPage() {
  const data = await api
    .cooccurrence(90, 2)
    .catch(() => ({ jobs_analyzed: 0, items: [] as Pair[], period_days: 90 }));

  const items = (data.items ?? []) as Pair[];

  return (
    <div className="space-y-4">
      <section className="card p-4">
        <h2 className="text-lg font-semibold">Skill co-occurrence</h2>
        <p className="text-sm opacity-70">
          Pairs of technologies that appear together in the same observed job. Lift &gt; 1 means
          more frequent than independence would predict. Not causation.
        </p>
        <p className="mt-2 text-xs opacity-60">
          Jobs analyzed: {String(data.jobs_analyzed ?? 0)} · window {String(data.period_days ?? 90)}{" "}
          days
        </p>
      </section>

      <section className="card overflow-x-auto p-4">
        <table className="w-full min-w-[640px] text-left text-sm">
          <thead>
            <tr className="border-b border-[var(--line)] text-xs uppercase opacity-60">
              <th className="py-2 pr-3">Tech A</th>
              <th className="py-2 pr-3">Tech B</th>
              <th className="py-2 pr-3">Support</th>
              <th className="py-2 pr-3">Lift</th>
              <th className="py-2 pr-3">Jaccard</th>
            </tr>
          </thead>
          <tbody>
            {items.length === 0 ? (
              <tr>
                <td colSpan={5} className="py-6 opacity-60">
                  No pairs yet — run Remotive/Arbeitnow or import jobs first.
                </td>
              </tr>
            ) : (
              items.slice(0, 80).map((row) => (
                <tr key={`${row.tech_a}-${row.tech_b}`} className="border-b border-[var(--line)]">
                  <td className="py-2 pr-3 font-medium">{row.tech_a}</td>
                  <td className="py-2 pr-3 font-medium">{row.tech_b}</td>
                  <td className="py-2 pr-3">{row.support}</td>
                  <td className="py-2 pr-3">{row.lift ?? "—"}</td>
                  <td className="py-2 pr-3">{row.jaccard ?? "—"}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </section>
    </div>
  );
}
