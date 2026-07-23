import type { Config } from "tailwindcss";
const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        surface: { DEFAULT: "#0a0e17", card: "#111827", elevated: "#1a1d2e", border: "#1f2937" },
        smi: { bearish: "#ef5350", neutral: "#ffa726", bullish: "#26a69a", extreme: "#00c853" },
        financial: { green: "#26a69a", red: "#ef5350", yellow: "#ffa726", blue: "#1a73e8", text: "#e2e8f0", muted: "#7c8db5", accent: "#3b82f6" },
      },
      fontFamily: { mono: ["JetBrains Mono", "Menlo", "monospace"], sans: ["Inter", "system-ui", "sans-serif"] },
    },
  },
  plugins: [],
};
export default config;
