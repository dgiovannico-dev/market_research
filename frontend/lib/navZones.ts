/** Four Atlas IA zones — grouping only; prefs still key off href. */

export type NavKey =
  | "executive"
  | "marketScan"
  | "myFocus"
  | "explorer"
  | "trends"
  | "skills"
  | "relations"
  | "rates"
  | "countries"
  | "languages"
  | "jobs"
  | "profile"
  | "applications"
  | "quality"
  | "alerts"
  | "report"
  | "sources"
  | "assistant";

export type NavZoneId = "explore" | "jobs" | "ops" | "research";

export type NavZoneLabelKey =
  | "zoneExplore"
  | "zoneJobs"
  | "zoneOps"
  | "zoneResearch";

export type NavItem = { href: string; key: NavKey };

export type NavZone = {
  id: NavZoneId;
  labelKey: NavZoneLabelKey;
  items: NavItem[];
};

export const NAV_ZONES: NavZone[] = [
  {
    id: "explore",
    labelKey: "zoneExplore",
    items: [
      { href: "/", key: "executive" },
      { href: "/market-scan", key: "marketScan" },
      { href: "/explorer", key: "explorer" },
      { href: "/trends", key: "trends" },
      { href: "/skills", key: "skills" },
      { href: "/relations", key: "relations" },
      { href: "/rates", key: "rates" },
      { href: "/countries", key: "countries" },
      { href: "/languages", key: "languages" },
    ],
  },
  {
    id: "jobs",
    labelKey: "zoneJobs",
    items: [
      { href: "/jobs", key: "jobs" },
      { href: "/profile", key: "profile" },
      { href: "/applications", key: "applications" },
    ],
  },
  {
    id: "ops",
    labelKey: "zoneOps",
    items: [
      { href: "/quality", key: "quality" },
      { href: "/sources", key: "sources" },
      { href: "/alerts", key: "alerts" },
    ],
  },
  {
    id: "research",
    labelKey: "zoneResearch",
    items: [
      { href: "/focus", key: "myFocus" },
      { href: "/report", key: "report" },
      { href: "/assistant", key: "assistant" },
    ],
  },
];

/** Flat list for prefs / legacy consumers — order follows zones. */
export const NAV_ITEMS: NavItem[] = NAV_ZONES.flatMap((zone) => zone.items);
