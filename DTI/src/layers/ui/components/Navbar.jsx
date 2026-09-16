import { NavLink } from "react-router-dom";
import { useTranslation } from "react-i18next";

const languageOptions = [
  { code: "en", label: "English" },
  { code: "hi", label: "हिंदी" },
  { code: "mr", label: "मराठी" },
  { code: "gu", label: "ગુજરાતી" },
  { code: "ta", label: "தமிழ்" },
  { code: "te", label: "తెలుగు" },
];

function Navbar() {
  const { t, i18n } = useTranslation();

  const links = [
    { to: "/", label: t("nav_home") },
    { to: "/scan", label: t("nav_scan") },
    { to: "/results", label: t("nav_results") },
    { to: "/dashboard", label: t("nav_dashboard", "Dashboard") },
    { to: "/weather", label: t("nav_weather") },
    { to: "/community", label: t("nav_community") },
    { to: "/login", label: t("nav_login") },
  ];

  const handleLanguageChange = (event) => {
    const next = event.target.value;
    i18n.changeLanguage(next);
    localStorage.setItem("plantvision-language", next);
  };

  const currentLanguage = languageOptions.find((item) => item.code === i18n.language)?.label || "English";

  return (
    <header className="sticky top-0 z-40 border-b border-white/10 bg-brand/80 backdrop-blur-xl">
      <nav className="page-shell flex items-center justify-between py-3">
        <div className="flex items-center gap-3">
          {/* Logo mark */}
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-leafPrimary to-leafSecondary shadow-glowPrimary">
            <svg className="h-5 w-5 text-brand" fill="currentColor" viewBox="0 0 20 20">
              <path d="M10 2C5.5 2 2 5.5 2 10s3.5 8 8 8 8-3.5 8-8-3.5-8-8-8zm-1 11.5c-2.2 0-4-1.8-4-4 0-1.5.8-2.8 2-3.5.3 1.8 1.5 3.2 3 3.8V11c0 .8-.4 1.5-1 2zm1-5.5c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2zm2 5.4c-.6-.5-1-1.2-1-2V9.8c1.5-.6 2.7-2 3-3.8 1.2.7 2 2 2 3.5 0 2.2-1.8 4-4 4z"/>
            </svg>
          </div>
          <p className="text-sm font-bold tracking-[0.12em] text-leafSecondary sm:text-base">
            PlantVision AI
          </p>
        </div>

        <div className="hidden items-center gap-1 md:flex">
          {links.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              className={({ isActive }) =>
                `rounded-full px-3 py-2 text-xs tracking-[0.10em] transition ${
                  isActive
                    ? "border border-leafPrimary/50 bg-leafPrimary/10 text-leafPrimary shadow-glowPrimary"
                    : "border border-transparent text-slate-300 hover:border-white/10 hover:bg-white/5"
                }`
              }
            >
              {link.label}
            </NavLink>
          ))}
        </div>

        <div className="glass-panel flex items-center gap-2 rounded-xl px-3 py-2 transition hover:border-leafPrimary/40">
          <span className="text-sm">🌐</span>
          <span className="hidden text-xs text-leafSecondary sm:block">{currentLanguage}</span>
          <select
            value={i18n.language}
            onChange={handleLanguageChange}
            className="rounded-lg border border-white/10 bg-brand px-2 py-1 text-xs text-textSoft outline-none transition hover:border-leafPrimary/50"
          >
            {languageOptions.map((option) => (
              <option key={option.code} value={option.code}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
      </nav>
    </header>
  );
}

export default Navbar;
