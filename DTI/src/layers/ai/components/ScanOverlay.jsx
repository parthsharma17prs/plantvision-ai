import { motion } from "framer-motion";

function ScanOverlay() {
  return (
    <motion.div
      animate={{ y: ["-10%", "110%"] }}
      transition={{ duration: 1.2, repeat: Infinity, ease: "linear" }}
      className="pointer-events-none absolute inset-x-4 h-10 bg-gradient-to-b from-transparent via-leafSecondary/45 to-transparent blur-sm"
    />
  );
}

export default ScanOverlay;
