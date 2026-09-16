/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        brand: "#061A13",
        leafPrimary: "#10B981",
        leafSecondary: "#34D399",
        textSoft: "#D1FAE5",
      },
      boxShadow: {
        glowPrimary: "0 0 40px rgba(16, 185, 129, 0.25)",
        glowSecondary: "0 0 40px rgba(52, 211, 153, 0.25)",
        panel: "0 30px 70px rgba(0, 0, 0, 0.5)",
      },
      backgroundImage: {
        mesh: "radial-gradient(at 15% 15%, rgba(16, 185, 129, 0.15) 0%, transparent 50%), radial-gradient(at 85% 85%, rgba(52, 211, 153, 0.1) 0%, transparent 50%), radial-gradient(at 50% 50%, rgba(6, 26, 19, 0.8) 0%, transparent 100%)",
      },
      keyframes: {
        floatY: {
          "0%, 100%": { transform: "translateY(0px)" },
          "50%": { transform: "translateY(-6px)" },
        },
        pulseGlow: {
          "0%, 100%": { boxShadow: "0 0 0 rgba(16,185,129,0)" },
          "50%": { boxShadow: "0 0 25px rgba(16,185,129,0.3)" },
        },
      },
      animation: {
        floatY: "floatY 6s ease-in-out infinite",
        pulseGlow: "pulseGlow 3s ease-in-out infinite",
      },
    },
  },
  plugins: [],
};
