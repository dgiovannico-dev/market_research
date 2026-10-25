export type StudyModality =
  | "employed_part_time"
  | "freelance_full_time"
  | "intensive";

export type StudyMilestone = {
  week: number;
  title: string;
  skills: string[];
  evidence_refs: string[];
  hours?: number | null;
};

export type StudyPlan = {
  title: string;
  horizon_weeks: number;
  modality: StudyModality;
  hours_per_week: number;
  stack_target: string[];
  milestones: StudyMilestone[];
  weekly_template: Array<Record<string, unknown>>;
  limits: string[];
  source: string;
};

export type StudyPlanResponse = {
  status: string;
  mode: string;
  reason?: string;
  plan: StudyPlan;
  evidence: Record<string, unknown>;
  error?: string;
};

export const STUDY_PLAN_KEY = "fmi:studyPlan:v1";

export type StoredStudyPlan = {
  plan: StudyPlan;
  evidence: Record<string, unknown>;
  saved_at: string;
};

export function loadStudyPlan(): StoredStudyPlan | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = localStorage.getItem(STUDY_PLAN_KEY);
    if (!raw) return null;
    return JSON.parse(raw) as StoredStudyPlan;
  } catch {
    return null;
  }
}

export function saveStudyPlan(plan: StudyPlan, evidence: Record<string, unknown>) {
  const payload: StoredStudyPlan = {
    plan,
    evidence,
    saved_at: new Date().toISOString(),
  };
  localStorage.setItem(STUDY_PLAN_KEY, JSON.stringify(payload));
  return payload;
}

/** Build a minimal ICS calendar from weekly_template repeating for horizon weeks. */
export function studyPlanToIcs(plan: StudyPlan): string {
  const lines = [
    "BEGIN:VCALENDAR",
    "VERSION:2.0",
    "PRODID:-FMI Study Advisor-EN",
    "CALSCALE:GREGORIAN",
  ];
  const start = new Date();
  start.setHours(0, 0, 0, 0);
  const weekdayMap: Record<string, number> = {
    mon: 1,
    tue: 2,
    wed: 3,
    thu: 4,
    fri: 5,
    sat: 6,
    sun: 0,
  };
  const template = plan.weekly_template || [];
  for (let w = 0; w < plan.horizon_weeks; w++) {
    for (const slot of template) {
      const wd = String(slot.weekday || "sat").toLowerCase();
      const targetDow = weekdayMap[wd] ?? 6;
      const day = new Date(start);
      day.setDate(start.getDate() + w * 7 + ((targetDow - start.getDay() + 7) % 7));
      const [sh, sm] = String(slot.start || "10:00").split(":").map(Number);
      const [eh, em] = String(slot.end || "12:00").split(":").map(Number);
      const dtStart = new Date(day);
      dtStart.setHours(sh || 10, sm || 0, 0, 0);
      const dtEnd = new Date(day);
      dtEnd.setHours(eh || 12, em || 0, 0, 0);
      const uid = `study-${w}-${wd}-${sh}@fmi.local`;
      lines.push(
        "BEGIN:VEVENT",
        `UID:${uid}`,
        `DTSTAMP:${formatIcs(new Date())}`,
        `DTSTART:${formatIcs(dtStart)}`,
        `DTEND:${formatIcs(dtEnd)}`,
        `SUMMARY:Study — ${plan.title}`,
        `DESCRIPTION:${(slot.label as string) || "study block"}`,
        "END:VEVENT",
      );
    }
  }
  lines.push("END:VCALENDAR");
  return lines.join("\r\n");
}

function formatIcs(d: Date): string {
  return d
    .toISOString()
    .replace(/[-:]/g, "")
    .replace(/\.\d{3}/, "");
}
