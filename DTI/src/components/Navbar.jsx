import { NavLink } from "react-router-dom";
import { motion } from "framer-motion";

const links = [
  { name: "Home", to: "/" },
  { name: "Dashboard", to: "/dashboard" },
  { name: "Upload", to: "/upload" },
  { name: "Results", to: "/results" },
  { name: "Login", to: "/login" },
];

function Navbar() {
  return (
    <header className="sticky top-0 z-40 border-b border-white/10 bg-brand/75 backdrop-blur-2xl">
      <nav className="page-shell flex items-center justify-between py-4">
        <motion.div
          initial={{ opacity: 0, y: -12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.35, ease: "easeOut" }}
          className="text-base font-bold tracking-[0.08em] sm:text-lg"
        >
          AgroNiddan <span className="text-leafSecondary">(LeafX)</span>
        </motion.div>

        <div className="hidden items-center gap-2 md:flex">
          {links.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              className={({ isActive }) =>
                `rounded-full px-4 py-2 text-xs font-medium tracking-[0.14em] transition ${
                  isActive
                    ? "border border-leafPrimary/45 bg-leafPrimary/10 text-leafPrimary shadow-glowPrimary"
                    : "border border-transparent text-slate-300 hover:border-white/10 hover:bg-white/5 hover:text-textSoft"
                }`
              }
            >
              {link.name}
            </NavLink>
          ))}
        </div>
      </nav>
    </header>
  );
}

export default Navbar;
