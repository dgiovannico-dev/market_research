export type StudyWeekday =
  | "mon"
  | "tue"
  | "wed"
  | "thu"
  | "fri"
  | "sat"
  | "sun";

export type BusySlotOrigin = "manual" | "calendar";

export type BusySlot = {
  weekday: StudyWeekday;
  start: string;
  end: string;
  label?: string;
  origin?: BusySlotOrigin;
};

export const STUDY_WEEKDAYS: StudyWeekday[] = [
  "mon",
  "tue",
  "wed",
  "thu",
  "fri",
  "sat",
  "sun",
];

export const BUSY_SLOTS_KEY = "fmi:studyBusySlots:v1";
export const CALENDAR_FEED_KEY = "fmi:studyCalendarFeed:v1";

const DEFAULT_BUSY: BusySlot[] = [
  { weekday: "mon", start: "09:00", end: "18:00", label: "work", origin: "manual" },
  { weekday: "tue", start: "09:00", end: "18:00", label: "work", origin: "manual" },
  { weekday: "wed", start: "09:00", end: "18:00", label: "work", origin: "manual" },
  { weekday: "thu", start: "09:00", end: "18:00", label: "work", origin: "manual" },
  { weekday: "fri", start: "09:00", end: "18:00", label: "work", origin: "manual" },
];

export function loadBusySlots(): BusySlot[] {
  if (typeof window === "undefined") return [...DEFAULT_BUSY];
  try {
    const raw = localStorage.getItem(BUSY_SLOTS_KEY);
    if (!raw) return [...DEFAULT_BUSY];
    const parsed = JSON.parse(raw) as BusySlot[];
    if (!Array.isArray(parsed)) return [...DEFAULT_BUSY];
    return parsed
      .filter(
        (s) =>
          s &&
          STUDY_WEEKDAYS.includes(s.weekday) &&
          typeof s.start === "string" &&
          typeof s.end === "string",
      )
      .map((s) => ({
        weekday: s.weekday,
        start: s.start,
        end: s.end,
        label: s.label || "busy",
        origin: s.origin === "calendar" ? "calendar" : "manual",
      }));
  } catch {
    return [...DEFAULT_BUSY];
  }
}

export function saveBusySlots(slots: BusySlot[]): void {
  if (typeof window === "undefined") return;
  try {
    localStorage.setItem(BUSY_SLOTS_KEY, JSON.stringify(slots));
  } catch {
    /* ignore */
  }
}

export function loadCalendarFeedUrl(): string {
  if (typeof window === "undefined") return "";
  try {
    return localStorage.getItem(CALENDAR_FEED_KEY) || "";
  } catch {
    return "";
  }
}

export function saveCalendarFeedUrl(url: string): void {
  if (typeof window === "undefined") return;
  try {
    if (url.trim()) localStorage.setItem(CALENDAR_FEED_KEY, url.trim());
    else localStorage.removeItem(CALENDAR_FEED_KEY);
  } catch {
    /* ignore */
  }
}

/** Replace calendar-origin slots; keep manual edits. */
export function mergeCalendarBusy(
  current: BusySlot[],
  fromCalendar: BusySlot[],
): BusySlot[] {
  const manual = current.filter((s) => s.origin !== "calendar");
  const imported = fromCalendar.map((s) => ({
    ...s,
    origin: "calendar" as const,
    label: s.label || "calendar",
  }));
  return [...manual, ...imported];
}
