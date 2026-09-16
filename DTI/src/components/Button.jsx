import { motion } from "framer-motion";

function Button({ children, variant = "primary", className = "", ...props }) {
  const shell = "group relative inline-flex items-center justify-center overflow-hidden rounded-full p-[1px]";

  const palette =
    variant === "secondary"
      ? "from-leafPrimary/90 via-leafSecondary/50 to-leafPrimary/90"
      : "from-leafSecondary/90 via-leafPrimary/50 to-leafSecondary/90";

  const innerTone =
    variant === "secondary"
      ? "bg-gradient-to-b from-[#0f1628] to-[#0a101f] text-leafPrimary"
      : "bg-gradient-to-b from-[#101927] to-[#0b121f] text-leafSecondary";

  return (
    <motion.button
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.97 }}
      transition={{ duration: 0.2, ease: "easeOut" }}
      className={`${shell} ${className}`}
      {...props}
    >
      <span className={`absolute inset-0 bg-gradient-to-r ${palette} opacity-90`} />
      <span className={`relative inline-flex min-w-[150px] items-center justify-center rounded-full px-6 py-3 text-sm font-semibold tracking-wide ${innerTone}`}>
        <motion.span
          initial={{ x: "-140%" }}
          whileHover={{ x: "170%" }}
          transition={{ duration: 0.95, ease: "easeInOut" }}
          className="pointer-events-none absolute inset-y-0 w-10 bg-white/30 blur-md"
        />
        <span className="relative z-10">{children}</span>
      </span>
    </motion.button>
  );
}

export default Button;
