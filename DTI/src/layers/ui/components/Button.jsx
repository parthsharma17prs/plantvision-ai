import { motion } from "framer-motion";

function Button({ children, variant = "primary", className = "", ...props }) {
  const tone =
    variant === "secondary"
      ? "from-leafPrimary/90 via-leafSecondary/40 to-leafPrimary/90"
      : "from-leafSecondary/90 via-leafPrimary/40 to-leafSecondary/90";

  return (
    <motion.button
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.97 }}
      transition={{ duration: 0.2 }}
      className={`group relative inline-flex overflow-hidden rounded-full p-[1px] ${className}`}
      {...props}
    >
      <span className={`absolute inset-0 bg-gradient-to-r ${tone}`} />
      <span className="relative inline-flex w-full min-w-[148px] items-center justify-center rounded-full bg-[#0f1524] px-6 py-3 text-sm font-semibold tracking-[0.08em] text-textSoft">
        <motion.span
          initial={{ x: "-150%" }}
          whileHover={{ x: "180%" }}
          transition={{ duration: 0.9, ease: "easeInOut" }}
          className="pointer-events-none absolute inset-y-0 w-10 bg-white/30 blur-md"
        />
        <span className="relative z-10">{children}</span>
      </span>
    </motion.button>
  );
}

export default Button;
