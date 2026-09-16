import { useEffect, useMemo, useState } from "react";
import { motion } from "framer-motion";
import { useTranslation } from "react-i18next";
import { fetchDiseaseRecommendation } from "../../services/api/recommendationApi";

function Results() {
  const { t } = useTranslation();
  const [image, setImage] = useState("");
  const [result, setResult] = useState(null);
  const [aiRecommendation, setAiRecommendation] = useState("");
  const [recLoading, setRecLoading] = useState(false);
  const [recError, setRecError] = useState("");

  useEffect(() => {
    setImage(localStorage.getItem("plantvision-image") || "");
    const raw = localStorage.getItem("plantvision-result");
    setResult(raw ? JSON.parse(raw) : null);
  }, []);

  useEffect(() => {
    if (!result?.disease) return undefined;
    let cancelled = false;
    const cacheKey = `plantvision-ai-rec:${result.disease}:${result.severity}:${result.plantHealth}:${result.confidence}`;
    const cached = sessionStorage.getItem(cacheKey);
    if (cached) {
      setAiRecommendation(cached);
      return undefined;
    }
    setRecLoading(true);
    setRecError("");
    fetchDiseaseRecommendation({
      disease: result.disease,
      severity: Number(result.severity) || 0,
      plantHealth: Number(result.plantHealth) || 0,
      confidence: Number(result.confidence) || 0,
      staticHint: String(result.suggestion || "").trim(),
    })
      .then((text) => {
        if (cancelled || !text) return;
        setAiRecommendation(text);
        sessionStorage.setItem(cacheKey, text);
      })
      .catch((err) => {
        if (!cancelled) {
          setRecError(err?.message || t("rec_ai_failed"));
        }
      })
      .finally(() => {
        if (!cancelled) setRecLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [result]);

  const healthScale = useMemo(() => {
    if (!result) return 0;
    return result.plantHealth / 100;
  }, [result]);

  const severityColor = (severity) => {
    const s = Number(severity) || 0;
    if (s >= 70) return "text-red-400";
    if (s >= 40) return "text-amber-400";
    return "text-emerald-400";
  };

  const confidenceBar = (conf) => {
    const c = Number(conf) || 0;
    if (c >= 90) return "from-emerald-500 to-green-400";
    if (c >= 50) return "from-amber-500 to-yellow-400";
    return "from-red-500 to-rose-400";
  };

  return (
    <section className="page-shell space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-3xl font-bold">{t("results_title")}</h2>
        {result && (
          <span className={`rounded-full px-3 py-1 text-xs font-semibold ${
            result.detected === false
              ? "bg-slate-700 text-slate-300"
              : result.disease?.toLowerCase().includes("healthy")
                ? "bg-emerald-900/50 text-emerald-300"
                : "bg-red-900/50 text-red-300"
          }`}>
            {result.detected === false ? "NO DETECTION" : result.disease?.toLowerCase().includes("healthy") ? "HEALTHY" : "DISEASED"}
          </span>
        )}
      </div>

      {!image || !result ? (
        <div className="glass-panel rounded-2xl p-8 text-center space-y-4">
          <div className="text-5xl">🔬</div>
          <p className="text-slate-300">{t("results_empty")}</p>
          <a href="/scan" className="inline-block rounded-full border border-leafPrimary/50 bg-leafPrimary/10 px-6 py-2 text-sm text-leafPrimary hover:bg-leafPrimary/20 transition">
            Go to Scan →
          </a>
        </div>
      ) : result.detected === false ? (
        // Honest "no detection" state
        <div className="glass-panel rounded-2xl p-8 text-center space-y-4">
          <div className="text-5xl">✅</div>
          <h3 className="text-xl font-bold text-emerald-400">No Disease Detected</h3>
          <p className="text-slate-300 text-sm">The AI model did not find any diseased regions in this image. The leaf appears healthy, or the image may not contain a clear leaf.</p>
          <div className="glass-panel rounded-xl overflow-hidden mt-4">
            <img src={result.annotatedImage || image} alt="Scan result" className="w-full object-cover max-h-64" />
          </div>
        </div>
      ) : (
        <>
          {/* Annotated Image */}
          <div className="glass-panel rounded-2xl p-4">
            <div className="relative overflow-hidden rounded-xl border border-leafPrimary/40">
              <img
                src={result.annotatedImage || image}
                alt={t("leaf_scan_alt")}
                className="aspect-video w-full object-cover"
              />
              {result.annotatedImage && result.annotatedImage !== image && (
                <div className="absolute top-2 left-2 rounded-full bg-leafPrimary/80 px-2 py-1 text-xs text-brand font-semibold">
                  AI Annotated
                </div>
              )}
            </div>
          </div>

          {/* Key Metrics */}
          <div className="grid gap-4 md:grid-cols-2">
            <div className="premium-card space-y-4">
              <p className="text-xs tracking-[0.2em] text-leafPrimary">DETECTION SUMMARY</p>

              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-slate-300">{t("disease_name")}</span>
                  <span className="text-sm font-semibold text-leafSecondary">{result.disease}</span>
                </div>

                <div className="flex justify-between items-center">
                  <span className="text-sm text-slate-300">Confidence</span>
                  <span className="text-sm font-semibold text-textSoft">{Number(result.confidence || 0).toFixed(1)}%</span>
                </div>

                {/* Confidence bar */}
                <div className="h-2 overflow-hidden rounded-full bg-white/10">
                  <motion.div
                    initial={{ scaleX: 0 }}
                    animate={{ scaleX: (Number(result.confidence) || 0) / 100 }}
                    className={`h-full origin-left rounded-full bg-gradient-to-r ${confidenceBar(result.confidence)}`}
                  />
                </div>

                <div className="flex justify-between items-center">
                  <span className="text-sm text-slate-300">{t("severity")}</span>
                  <span className={`text-sm font-semibold ${severityColor(result.severity)}`}>
                    {Number(result.severity || 0).toFixed(1)}%
                  </span>
                </div>

                <div className="flex justify-between items-center">
                  <span className="text-sm text-slate-300">{t("plant_health")}</span>
                  <span className="text-sm font-semibold text-textSoft">{Number(result.plantHealth || 0).toFixed(1)}%</span>
                </div>

                {/* Health bar */}
                <div className="h-2 overflow-hidden rounded-full bg-white/10">
                  <motion.div
                    initial={{ scaleX: 0 }}
                    animate={{ scaleX: healthScale }}
                    className="h-full origin-left rounded-full bg-gradient-to-r from-leafPrimary to-leafSecondary"
                  />
                </div>

                {/* Bounding box info */}
                {result.detections?.[0]?.bbox && (
                  <div className="pt-2 border-t border-white/10">
                    <p className="text-xs text-slate-400">
                      Detection box: [{result.detections[0].bbox.map(v => Math.round(v)).join(", ")}]
                    </p>
                  </div>
                )}
              </div>
            </div>

            {/* Recommendation */}
            <div className="premium-card space-y-3">
              <p className="text-xs tracking-[0.2em] text-leafPrimary">{t("recommendation")}</p>
              {recLoading && (
                <div className="flex items-center gap-2 mt-3">
                  <div className="h-1.5 w-1.5 rounded-full bg-leafPrimary animate-bounce" />
                  <div className="h-1.5 w-1.5 rounded-full bg-leafPrimary animate-bounce" style={{ animationDelay: "0.15s" }} />
                  <div className="h-1.5 w-1.5 rounded-full bg-leafPrimary animate-bounce" style={{ animationDelay: "0.3s" }} />
                  <p className="text-sm text-slate-400">{t("rec_loading")}</p>
                </div>
              )}
              {recError && !aiRecommendation && (
                <p className="mt-3 text-sm text-amber-300/90">⚠ {recError}</p>
              )}
              {aiRecommendation ? (
                <div className="mt-2 whitespace-pre-wrap text-sm leading-relaxed text-slate-200">
                  {aiRecommendation}
                </div>
              ) : (
                !recLoading && (
                  <p className="mt-2 text-sm leading-relaxed text-slate-200">
                    {result.suggestion || t("rec_empty_fallback")}
                  </p>
                )
              )}
              {aiRecommendation && result.suggestion && (
                <p className="mt-4 border-t border-white/10 pt-3 text-xs text-slate-500">
                  <span className="text-leafPrimary/80">{t("rec_quick_tip")}: </span>
                  {result.suggestion}
                </p>
              )}
            </div>
          </div>

          {/* All detections if multiple */}
          {result.detections && result.detections.length > 1 && (
            <div className="glass-panel rounded-2xl p-5 space-y-3">
              <p className="text-xs tracking-[0.2em] text-leafPrimary">ALL DETECTIONS ({result.detections.length})</p>
              <div className="space-y-2">
                {result.detections.map((det, i) => (
                  <div key={i} className="flex items-center justify-between rounded-xl bg-white/5 px-4 py-2">
                    <span className="text-sm text-slate-200">{det.disease}</span>
                    <span className="text-sm text-leafSecondary">{Number(det.confidence || 0).toFixed(1)}%</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </section>
  );
}

export default Results;
