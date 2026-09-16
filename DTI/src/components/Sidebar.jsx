import { useState } from "react";
import { NavLink } from "react-router-dom";
import { motion } from "framer-motion";

const items = [
  { to: "/dashboard", label: "Overview", icon: "O" },
  { to: "/upload", label: "Upload", icon: "U" },
  { to: "/results", label: "Results", icon: "R" },
];

function Sidebar() {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <>
      <motion.aside
        animate={{ width: collapsed ? 92 : 244 }}
        transition={{ duration: 0.24, ease: "easeOut" }}
        className="glass-panel hidden h-fit rounded-2xl p-4 lg:block"
      >
        <button
          type="button"
          onClick={() => setCollapsed((prev) => !prev)}
          className="mb-4 w-full rounded-lg border border-white/10 bg-white/[0.04] px-3 py-2 text-left text-xs font-semibold tracking-[0.16em] text-slate-200 transition hover:border-leafSecondary/45 hover:text-leafSecondary"
        >
          {collapsed ? "EXPAND" : "COLLAPSE"}
        </button>

        <div className="space-y-2">
          {items.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-xl px-3 py-3 text-sm transition ${
                  isActive
                    ? "border border-leafSecondary/45 bg-leafSecondary/10 text-leafSecondary shadow-glowSecondary"
                    : "border border-transparent text-slate-300 hover:border-white/10 hover:bg-white/5 hover:text-textSoft"
                }`
              }
            >
              <span className="inline-flex h-7 w-7 items-center justify-center rounded-full border border-white/20 text-[10px] font-bold tracking-wider">
                {item.icon}
              </span>
              {!collapsed && <span className="tracking-wide">{item.label}</span>}
            </NavLink>
          ))}
        </div>
      </motion.aside>

      <nav className="glass-panel fixed inset-x-4 bottom-4 z-40 rounded-2xl p-2 lg:hidden">
        <div className="grid grid-cols-3 gap-2">
          {items.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `rounded-xl px-3 py-2 text-center text-xs font-semibold tracking-wide transition ${
                  isActive
                    ? "bg-leafPrimary/20 text-leafPrimary"
                    : "text-slate-300 hover:bg-white/5 hover:text-textSoft"
                }`
              }
            >
              {item.label}
            </NavLink>
          ))}
        </div>
      </nav>
    </>
  );
}

export default Sidebar;
