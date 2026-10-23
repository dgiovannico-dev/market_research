import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    // FSD layers — utilities used only here must be scanned or CSS silently drops.
    "./shared/**/*.{ts,tsx}",
    "./widgets/**/*.{ts,tsx}",
    "./features/**/*.{ts,tsx}",
    "./entities/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        ink: "var(--ink)",
        paper: "var(--paper)",
        signal: "var(--signal)",
        rise: "var(--rise)",
        cool: "var(--cool)",
        panel: "var(--card)",
        accent: "var(--signal)",
        warn: "var(--warn)",
      },
      fontFamily: {
        sans: ["var(--font-sans)", "Source Sans 3", "ui-sans-serif", "system-ui", "sans-serif"],
        display: ["var(--font-display)", "Syne", "ui-sans-serif", "system-ui", "sans-serif"],
        mono: ["var(--font-mono)", "IBM Plex Mono", "ui-monospace", "monospace"],
      },
    },
  },
  plugins: [],
};

export default config;
