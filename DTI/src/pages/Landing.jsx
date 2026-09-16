import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import Button from "../components/Button";

function Landing() {
  return (
    <section className="relative overflow-hidden">
      <motion.div
        animate={{ backgroundPosition: ["0% 50%", "100% 50%", "0% 50%"] }}
        transition={{ duration: 18, repeat: Infinity, ease: "linear" }}
        className="pointer-events-none absolute inset-0 bg-[linear-gradient(120deg,rgba(0,255,156,0.08),rgba(0,207,255,0.08),rgba(0,255,156,0.08))] bg-[length:200%_200%]"
      />

      <div className="page-shell relative flex min-h-[calc(100vh-80px)] flex-col items-center justify-center text-center">
        <motion.p
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.45 }}
          className="mb-4 text-xs font-semibold tracking-[0.28em] text-leafPrimary"
        >
          AI AGRI INTELLIGENCE PLATFORM
        </motion.p>

        <motion.h1
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.55, delay: 0.05 }}
          className="max-w-5xl text-4xl font-extrabold tracking-tight sm:text-5xl lg:text-7xl"
        >
          AgroNiddan <span className="text-leafSecondary">- AI for Smart Farming</span>
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.55, delay: 0.12 }}
          className="mt-6 max-w-2xl text-sm leading-relaxed text-slate-300 sm:text-base"
        >
          Enterprise-grade plant disease detection with explainable results, intelligent severity scoring, and treatment recommendations for precision agriculture teams.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.55, delay: 0.18 }}
          className="mt-10 flex flex-wrap items-center justify-center gap-4"
        >
          <Link to="/upload">
            <Button>Start Scanning</Button>
          </Link>
          <Link to="/dashboard">
            <Button variant="secondary">View Demo</Button>
          </Link>
        </motion.div>

        <motion.div
          animate={{ y: [0, 8, 0], opacity: [0.5, 1, 0.5] }}
          transition={{ duration: 2.2, repeat: Infinity }}
          className="absolute bottom-8 flex flex-col items-center gap-2 text-[11px] tracking-[0.2em] text-slate-400"
        >
          <span>SCROLL</span>
          <span className="h-9 w-5 rounded-full border border-white/20 p-1">
            <span className="block h-2 w-2 rounded-full bg-leafSecondary" />
          </span>
        </motion.div>
      </div>
    </section>
  );
}

export default Landing;
