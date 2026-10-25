export type LocalUserProfile = {
  display_name: string;
  residence_country: string;
  target_rate_amount: string;
  rate_currency: string;
  rate_unit: string;
  /** Canonical technology names owned by the user */
  skills: string[];
  /** Optional cert names the user holds (local only) */
  certifications: string[];
};

export const PROFILE_STORAGE_KEY = "fmi:userProfile:v1";

export const DEFAULT_LOCAL_PROFILE: LocalUserProfile = {
  display_name: "",
  residence_country: "",
  target_rate_amount: "",
  rate_currency: "EUR",
  rate_unit: "day",
  skills: [],
  certifications: [],
};

export function loadLocalProfile(): LocalUserProfile {
  if (typeof window === "undefined") return { ...DEFAULT_LOCAL_PROFILE };
  try {
    const raw = localStorage.getItem(PROFILE_STORAGE_KEY);
    if (!raw) return { ...DEFAULT_LOCAL_PROFILE };
    const parsed = JSON.parse(raw) as Partial<LocalUserProfile>;
    return {
      ...DEFAULT_LOCAL_PROFILE,
      ...parsed,
      skills: Array.isArray(parsed.skills) ? parsed.skills.map(String) : [],
      certifications: Array.isArray(parsed.certifications)
        ? parsed.certifications.map(String)
        : [],
    };
  } catch {
    return { ...DEFAULT_LOCAL_PROFILE };
  }
}

export function saveLocalProfile(profile: LocalUserProfile): void {
  if (typeof window === "undefined") return;
  try {
    localStorage.setItem(PROFILE_STORAGE_KEY, JSON.stringify(profile));
  } catch {
    /* ignore quota */
  }
}

export function parseSkillsCsv(raw: string): string[] {
  return raw
    .split(/[,;\n]/)
    .map((s) => s.trim())
    .filter(Boolean);
}
