import { motion } from "framer-motion";
import { useLocation } from "react-router-dom";

function PageTransition({ children }) {
  const location = useLocation();

  return (
    <motion.main
      key={location.pathname}
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -8 }}
      transition={{ duration: 0.3, ease: "easeOut" }}
      className="relative pb-24 md:pb-8"
    >
      {children}
    </motion.main>
  );
}

export default PageTransition;
