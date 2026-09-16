import { motion } from "framer-motion";

function Loader({ text = "Analyzing leaf image with AI..." }) {
  return (
    <div className="glass-panel relative overflow-hidden rounded-2xl p-6">
      <div className="absolute inset-0 bg-gradient-to-r from-transparent via-leafPrimary/10 to-transparent" />
      <motion.div
        animate={{ x: ["-120%", "120%"] }}
        transition={{ duration: 1.3, repeat: Infinity, ease: "linear" }}
        className="absolute inset-y-0 w-1/4 bg-leafSecondary/25 blur-lg"
      />
      <motion.div
        animate={{ opacity: [0.55, 1, 0.55] }}
        transition={{ duration: 1.8, repeat: Infinity }}
        className="relative z-10 flex items-center gap-3"
      >
        <span className="h-2.5 w-2.5 rounded-full bg-leafSecondary" />
        <p className="text-sm text-slate-200">{text}</p>
      </motion.div>
    </div>
  );
}

export default Loader;
