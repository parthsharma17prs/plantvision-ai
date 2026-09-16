import { useEffect, useMemo, useState } from "react";
import { motion } from "framer-motion";
import Sidebar from "../components/Sidebar";

function Results() {
  const [image, setImage] = useState("");
  const [result, setResult] = useState(null);

  useEffect(() => {
    const storedImage = localStorage.getItem("leafx-image") || "";
    const storedResult = localStorage.getItem("leafx-result");
    setImage(storedImage);
    setResult(storedResult ? JSON.parse(storedResult) : null);
  }, []);

  const severityColor = useMemo(() => {
    if (!result) return "from-leafPrimary to-leafSecondary";
    return result.severity > 75 ? "from-rose-500 to-leafSecondary" : "from-leafPrimary to-leafSecondary";
  }, [result]);

  return (
    <section className="page-shell">
      <div className="grid gap-6 lg:grid-cols-[244px_1fr]">
        <Sidebar />

        <div className="space-y-6">
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">AI Detection Results</h2>

          {!image || !result ? (
            <div className="glass-panel rounded-2xl p-6 text-slate-300">No scan result found. Upload an image first.</div>
          ) : (
            <>
              <div className="glass-panel rounded-2xl p-4">
                <div className="relative overflow-hidden rounded-xl border border-white/10">
                  <img src={image} alt="Scanned leaf" className="max-h-[500px] w-full object-cover" />
                  {result.boxes.map((box, index) => (
                    <motion.div
                      key={`${box}-${index}`}
                      initial={{ opacity: 0.45 }}
                      animate={{ opacity: [0.5, 1, 0.5] }}
                      transition={{ duration: 1.6, repeat: Infinity, delay: index * 0.2 }}
                      className={`absolute border-2 border-leafSecondary shadow-glowSecondary ${box}`}
                    />
                  ))}
                </div>
              </div>

              <div className="grid gap-4 xl:grid-cols-[1.1fr_1fr]">
                <div className="glass-panel rounded-2xl p-6">
                  <p className="text-xs uppercase tracking-[0.22em] text-slate-400">Disease Name</p>
                  <h3 className="mt-2 text-2xl font-bold text-leafSecondary">{result.disease}</h3>

                  <div className="mt-6">
                    <div className="mb-2 flex items-center justify-between text-sm">
                      <span className="text-slate-300">Severity</span>
                      <span className="text-textSoft">{result.severity}%</span>
                    </div>
                    <div className="h-3 overflow-hidden rounded-full bg-white/10">
                      <motion.div
                        initial={{ scaleX: 0 }}
                        animate={{ scaleX: result.severity / 100 }}
                        transition={{ duration: 1.1, ease: "easeOut" }}
                        className={`h-full origin-left bg-gradient-to-r ${severityColor}`}
                      />
                    </div>
                  </div>
                </div>

                <div className="glass-panel rounded-2xl p-6">
                  <p className="text-xs uppercase tracking-[0.22em] text-leafPrimary">Recommendation</p>
                  <p className="mt-3 text-sm leading-relaxed text-slate-200">{result.suggestion}</p>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </section>
  );
}

export default Results;
