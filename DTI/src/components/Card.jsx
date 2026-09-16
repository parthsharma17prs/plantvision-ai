import { motion } from "framer-motion";

function Card({ title, value, subtitle, accent = "blue" }) {
  const accentTone = accent === "green" ? "text-leafSecondary" : "text-leafPrimary";

  return (
    <motion.article
      whileHover={{ y: -4, scale: 1.03 }}
      transition={{ duration: 0.24, ease: "easeOut" }}
      className="premium-card"
    >
      <p className="text-[11px] uppercase tracking-[0.22em] text-slate-400">{title}</p>
      <motion.h3
        initial={{ opacity: 0.85 }}
        whileHover={{ opacity: 1 }}
        className={`mt-3 text-3xl font-bold tracking-tight ${accentTone}`}
      >
        {value}
      </motion.h3>
      <p className="mt-2 text-sm leading-relaxed text-slate-300">{subtitle}</p>
    </motion.article>
  );
}

export default Card;
