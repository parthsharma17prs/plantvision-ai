import { motion } from "framer-motion";

function Card({ title, value, subtitle }) {
  return (
    <motion.article
      whileHover={{ y: -4, scale: 1.03 }}
      transition={{ duration: 0.2 }}
      className="premium-card"
    >
      <p className="text-[11px] uppercase tracking-[0.2em] text-slate-400">{title}</p>
      <h3 className="mt-3 text-3xl font-bold text-textSoft">{value}</h3>
      <p className="mt-2 text-sm text-slate-300">{subtitle}</p>
    </motion.article>
  );
}

export default Card;
