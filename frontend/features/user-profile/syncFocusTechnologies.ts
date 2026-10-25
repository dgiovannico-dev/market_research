import {
  loadDashboardPrefs,
  saveDashboardPrefs,
} from "@/features/dashboard-prefs/model/prefs";

/**
 * Optional mirror: local profile skills → dashboard prefs.focus_technologies.
 * Does not wipe existing focus entries that are not in skills; unions them.
 */
export function syncFocusTechnologiesFromSkills(skills: string[]): void {
  if (typeof window === "undefined") return;
  const cleaned = skills.map((s) => s.trim()).filter(Boolean);
  if (cleaned.length === 0) return;
  try {
    const prefs = loadDashboardPrefs();
    const existing = new Set(
      prefs.focus_technologies.map((t) => t.toLowerCase()),
    );
    const merged = [...prefs.focus_technologies];
    for (const skill of cleaned) {
      if (!existing.has(skill.toLowerCase())) {
        merged.push(skill);
        existing.add(skill.toLowerCase());
      }
    }
    if (merged.length === prefs.focus_technologies.length) return;
    saveDashboardPrefs({ ...prefs, focus_technologies: merged });
  } catch {
    /* ignore */
  }
}
