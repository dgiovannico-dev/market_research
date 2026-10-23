/** Read signal-desk chart colors from CSS variables (with SSR-safe fallbacks). */

export type ChartTheme = {
  signal: string;
  rise: string;
  cool: string;
  ink: string;
  line: string;
  card: string;
  mono: string;
};

const FALLBACKS: ChartTheme = {
  signal: "#0f766e",
  rise: "#047857",
  cool: "#0369a1",
  ink: "#0c1b1a",
  line: "#c9d9d5",
  card: "#ffffff",
  mono: '"IBM Plex Mono", ui-monospace, monospace',
};

function readVar(name: string, fallback: string): string {
  if (typeof window === "undefined") return fallback;
  const value = getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  return value || fallback;
}

export function chartTheme(): ChartTheme {
  return {
    signal: readVar("--signal", FALLBACKS.signal),
    rise: readVar("--rise", FALLBACKS.rise),
    cool: readVar("--cool", FALLBACKS.cool),
    ink: readVar("--ink", FALLBACKS.ink),
    line: readVar("--line", FALLBACKS.line),
    card: readVar("--card", FALLBACKS.card),
    mono: readVar("--mono", FALLBACKS.mono),
  };
}

export function prefersReducedMotion(): boolean {
  if (typeof window === "undefined") return false;
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

export function chartAnimationMs(): number {
  return prefersReducedMotion() ? 0 : 320;
}

