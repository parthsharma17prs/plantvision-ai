import { NavLink } from "react-router-dom";
import { useTranslation } from "react-i18next";

function BottomNav() {
  const { t } = useTranslation();

  const items = [
    { to: "/scan", label: t("nav_scan") },
    { to: "/results", label: t("nav_results") },
    { to: "/weather", label: t("nav_weather") },
    { to: "/community", label: t("nav_community") },
  ];

  return (
    <nav className="glass-panel fixed inset-x-4 bottom-4 z-40 rounded-2xl p-2 md:hidden">
      <div className="grid grid-cols-4 gap-2">
        {items.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `rounded-lg px-2 py-2 text-center text-xs tracking-wide ${
                isActive ? "bg-leafSecondary/20 text-leafSecondary" : "text-slate-300"
              }`
            }
          >
            {item.label}
          </NavLink>
        ))}
      </div>
    </nav>
  );
}

export default BottomNav;
