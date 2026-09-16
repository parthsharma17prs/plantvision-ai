import { useEffect, useMemo, useState } from "react";
import { motion } from "framer-motion";
import { useTranslation } from "react-i18next";
import { fetchDiseaseRecommendation } from "../../services/api/recommendationApi";
import { getLatestResult, diagnosePest, diagnoseNutrition } from "../../services/api/predictionApi";

function Results() {
  const { t } = useTranslation();
  const [image, setImage] = useState("");
  const [result, setResult] = useState(null);
  const [activeTab, setActiveTab] = useState("disease"); // "disease" | "pest" | "nutrition"

  // Disease AI recommendation state
  const [aiRecommendation, setAiRecommendation] = useState("");
  const [recLoading, setRecLoading] = useState(false);
  const [recError, setRecError] = useState("");

  // Pest and Nutrition sub-engine states
  const [pestData, setPestData] = useState(null);
  const [loadingPest, setLoadingPest] = useState(false);
  const [nutritionData, setNutritionData] = useState(null);
  const [loadingNutrition, setLoadingNutrition] = useState(false);

  useEffect(() => {
    const storedImg = localStorage.getItem("plantvision-image") || "";
    const raw = localStorage.getItem("plantvision-result");
    if (raw) {
      try {
        const parsed = JSON.parse(raw);
        setImage(storedImg || parsed.annotatedImage || "");
        setResult(parsed);
        if (parsed.pest_analysis) setPestData(parsed.pest_analysis);
        if (parsed.nutrition_analysis) setNutritionData(parsed.nutrition_analysis);
      } catch (e) {
        console.error("Failed to parse stored result", e);
      }
    } else {
      getLatestResult()
        .then((latest) => {
          if (latest?.success && latest.disease) {
            setResult(latest);
            if (latest.annotatedImage) setImage(latest.annotatedImage);
            if (latest.pest_analysis) setPestData(latest.pest_analysis);
            if (latest.nutrition_analysis) setNutritionData(latest.nutrition_analysis);
          }
        })
        .catch(() => {});
    }
  }, []);

  // Fetch disease AI recommendation
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
  }, [result, t]);

  // Lazy fetch Pest data if missing from scan
  useEffect(() => {
    if (result && !pestData && !loadingPest && image && image.startsWith("data:")) {
      setLoadingPest(true);
      diagnosePest(image, result.disease)
        .then((res) => {
          if (res?.pest_analysis) setPestData(res.pest_analysis);
          else if (res?.pest_name) setPestData(res);
        })
        .catch(() => {})
        .finally(() => setLoadingPest(false));
    }
  }, [result, pestData, loadingPest, image]);

  // Lazy fetch Nutrition data if missing from scan
  useEffect(() => {
    if (result && !nutritionData && !loadingNutrition && image && image.startsWith("data:")) {
      setLoadingNutrition(true);
      diagnoseNutrition(image, result.disease)
        .then((res) => {
          if (res?.nutrition_analysis) setNutritionData(res.nutrition_analysis);
          else if (res?.primary_deficiency) setNutritionData(res);
        })
        .catch(() => {})
        .finally(() => setLoadingNutrition(false));
    }
  }, [result, nutritionData, loadingNutrition, image]);

  const healthScale = useMemo(() => {
    if (!result) return 0;
    return (result.plantHealth || 0) / 100;
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

  const pestRiskBadge = (rating) => {
    const r = (rating || "None").toLowerCase();
    if (r.includes("crit") || r.includes("sev") || r.includes("high")) {
      return "bg-red-500/20 text-red-400 border-red-500/30";
    }
    if (r.includes("mod")) {
      return "bg-amber-500/20 text-amber-400 border-amber-500/30";
    }
    if (r.includes("low")) {
      return "bg-yellow-500/20 text-yellow-300 border-yellow-500/30";
    }
    return "bg-emerald-500/20 text-emerald-400 border-emerald-500/30";
  };

  return (
    <section className="page-shell space-y-6">
      {/* ── Top Header & Global Status Badges ── */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">{t("results_title")}</h2>
          <p className="text-xs text-slate-400 mt-1 font-mono">
            Multi-Spectral Agricultural Intelligence Console
          </p>
        </div>

        {result && (
          <div className="flex flex-wrap items-center gap-2">
            {/* Disease Status Badge */}
            <span
              className={`rounded-full px-3 py-1 text-xs font-semibold border font-mono ${
                result.detected === false
                  ? "bg-slate-800 text-slate-300 border-slate-700"
                  : result.disease?.toLowerCase().includes("healthy")
                  ? "bg-emerald-900/40 text-emerald-300 border-emerald-500/30"
                  : "bg-red-900/40 text-red-300 border-red-500/30"
              }`}
            >
              {result.detected === false
                ? "NO PATHOLOGY"
                : result.disease?.toLowerCase().includes("healthy")
                ? "CANOPY HEALTHY"
                : "PATHOLOGY DETECTED"}
            </span>

            {/* Pest Risk Badge */}
            {pestData && (
              <span
                className={`rounded-full px-3 py-1 text-xs font-semibold border font-mono ${pestRiskBadge(
                  pestData.risk_level || pestData.severity_rating
                )}`}
              >
                Pest Risk: {pestData.risk_level || pestData.severity_rating || "Low"}
              </span>
            )}

            {/* Nutrition Badge */}
            {nutritionData && (
              <span className="rounded-full px-3 py-1 text-xs font-semibold border bg-emerald-950/40 text-leafSecondary border-leafSecondary/30 font-mono">
                Nutrient Status: {nutritionData.severity || "Evaluated"}
              </span>
            )}
          </div>
        )}
      </div>

      {!result ? (
        <div className="glass-panel rounded-2xl p-8 text-center space-y-4">
          <div className="text-5xl">🔬</div>
          <p className="text-slate-300">{t("results_empty")}</p>
          <a
            href="/scan"
            className="inline-block rounded-full border border-leafPrimary/50 bg-leafPrimary/10 px-6 py-2 text-sm text-leafPrimary hover:bg-leafPrimary/20 transition"
          >
            Go to Scan →
          </a>
        </div>
      ) : (
        <>
          {/* ── Annotated Image Viewport ── */}
          {(result.annotatedImage || image) && (
            <div className="glass-panel rounded-2xl p-4 border border-white/10">
              <div className="relative overflow-hidden rounded-xl border border-leafPrimary/30 bg-black/40">
                <img
                  src={result.annotatedImage || image}
                  alt={t("leaf_scan_alt")}
                  className="aspect-video w-full object-cover max-h-[400px]"
                />
                <div className="absolute top-3 left-3 flex items-center gap-2">
                  <span className="rounded-full bg-leafPrimary/90 px-3 py-1 text-xs text-brand font-bold shadow-lg backdrop-blur-md">
                    YOLOv8 Spatial Bounds Active
                  </span>
                </div>
                <div className="absolute bottom-3 right-3 bg-black/70 backdrop-blur-md border border-white/10 rounded-lg px-3 py-1 text-[11px] font-mono text-slate-300">
                  Resolution: 640x640 Multi-Spectral Input
                </div>
              </div>
            </div>
          )}

          {/* ── Engine Navigation Tab Switcher ── */}
          <div className="flex border-b border-white/10 gap-2 overflow-x-auto pb-1">
            <button
              onClick={() => setActiveTab("disease")}
              className={`px-5 py-3 text-xs font-semibold uppercase tracking-wider rounded-xl transition flex items-center gap-2.5 border ${
                activeTab === "disease"
                  ? "bg-leafPrimary/15 text-leafPrimary border-leafPrimary/40 shadow-sm"
                  : "bg-white/[0.02] text-slate-400 border-transparent hover:text-slate-200 hover:bg-white/[0.05]"
              }`}
            >
              <span>🔬</span>
              <span>1. Pathology & Disease</span>
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-black/40 border border-white/10 font-mono">
                {Number(result.confidence || 0).toFixed(0)}%
              </span>
            </button>

            <button
              onClick={() => setActiveTab("pest")}
              className={`px-5 py-3 text-xs font-semibold uppercase tracking-wider rounded-xl transition flex items-center gap-2.5 border ${
                activeTab === "pest"
                  ? "bg-leafSecondary/15 text-leafSecondary border-leafSecondary/40 shadow-sm"
                  : "bg-white/[0.02] text-slate-400 border-transparent hover:text-slate-200 hover:bg-white/[0.05]"
              }`}
            >
              <span>🐛</span>
              <span>2. Pest Detection Adapter</span>
              {pestData && (
                <span
                  className={`text-[10px] px-1.5 py-0.5 rounded border font-mono ${pestRiskBadge(
                    pestData.risk_level || pestData.severity_rating
                  )}`}
                >
                  {pestData.risk_level || pestData.severity_rating || "Active"}
                </span>
              )}
            </button>

            <button
              onClick={() => setActiveTab("nutrition")}
              className={`px-5 py-3 text-xs font-semibold uppercase tracking-wider rounded-xl transition flex items-center gap-2.5 border ${
                activeTab === "nutrition"
                  ? "bg-emerald-500/15 text-emerald-400 border-emerald-500/40 shadow-sm"
                  : "bg-white/[0.02] text-slate-400 border-transparent hover:text-slate-200 hover:bg-white/[0.05]"
              }`}
            >
              <span>🧪</span>
              <span>3. Nutrition Deficiency Engine</span>
              {nutritionData && (
                <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-950/60 border border-emerald-500/30 text-emerald-300 font-mono">
                  {nutritionData.element_key || "Spectrum"}
                </span>
              )}
            </button>
          </div>

          {/* ─────────────────────────────────────────────────────────────
              TAB 1: PATHOLOGY & DISEASE
          ───────────────────────────────────────────────────────────── */}
          {activeTab === "disease" && (
            <motion.div
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.2 }}
              className="space-y-6"
            >
              <div className="grid gap-5 md:grid-cols-2">
                {/* Detection Metrics */}
                <div className="premium-card space-y-4">
                  <div className="flex items-center justify-between">
                    <p className="text-xs tracking-[0.2em] text-leafPrimary font-mono">PATHOLOGY TELEMETRY</p>
                    <span className="text-[10px] text-slate-400 font-mono">YOLOv8x-Det</span>
                  </div>

                  <div className="space-y-3.5">
                    <div className="flex justify-between items-center pb-2 border-b border-white/5">
                      <span className="text-sm text-slate-300">{t("disease_name")}</span>
                      <span className="text-sm font-semibold text-leafSecondary">{result.disease}</span>
                    </div>

                    <div className="space-y-1">
                      <div className="flex justify-between items-center text-xs">
                        <span className="text-slate-400">Confidence Score</span>
                        <span className="font-mono text-slate-200">{Number(result.confidence || 0).toFixed(1)}%</span>
                      </div>
                      <div className="h-2 overflow-hidden rounded-full bg-white/10">
                        <motion.div
                          initial={{ scaleX: 0 }}
                          animate={{ scaleX: (Number(result.confidence) || 0) / 100 }}
                          className={`h-full origin-left rounded-full bg-gradient-to-r ${confidenceBar(
                            result.confidence
                          )}`}
                        />
                      </div>
                    </div>

                    <div className="space-y-1">
                      <div className="flex justify-between items-center text-xs">
                        <span className="text-slate-400">{t("severity")}</span>
                        <span className={`font-mono font-semibold ${severityColor(result.severity)}`}>
                          {Number(result.severity || 0).toFixed(1)}%
                        </span>
                      </div>
                      <div className="h-2 overflow-hidden rounded-full bg-white/10">
                        <motion.div
                          initial={{ scaleX: 0 }}
                          animate={{ scaleX: (Number(result.severity) || 0) / 100 }}
                          className="h-full origin-left rounded-full bg-gradient-to-r from-emerald-500 via-amber-500 to-red-500"
                        />
                      </div>
                    </div>

                    <div className="space-y-1">
                      <div className="flex justify-between items-center text-xs">
                        <span className="text-slate-400">{t("plant_health")}</span>
                        <span className="font-mono text-slate-200">{Number(result.plantHealth || 0).toFixed(1)}%</span>
                      </div>
                      <div className="h-2 overflow-hidden rounded-full bg-white/10">
                        <motion.div
                          initial={{ scaleX: 0 }}
                          animate={{ scaleX: healthScale }}
                          className="h-full origin-left rounded-full bg-gradient-to-r from-leafPrimary to-leafSecondary"
                        />
                      </div>
                    </div>

                    {/* Bounding box info */}
                    {result.detections?.[0]?.bbox && (
                      <div className="pt-2 border-t border-white/10 flex items-center justify-between text-xs font-mono text-slate-400">
                        <span>Spatial Bounds [X1, Y1, X2, Y2]</span>
                        <span className="text-slate-300">
                          [{result.detections[0].bbox.map((v) => Math.round(v)).join(", ")}]
                        </span>
                      </div>
                    )}
                  </div>
                </div>

                {/* AI Agronomist Clinical Protocol */}
                <div className="premium-card space-y-3">
                  <div className="flex items-center justify-between">
                    <p className="text-xs tracking-[0.2em] text-leafPrimary font-mono">CLINICAL PROTOCOL</p>
                    <span className="text-[10px] text-leafSecondary font-mono">Gemini Vision 2.5</span>
                  </div>

                  {recLoading && (
                    <div className="flex items-center gap-2 py-4">
                      <div className="h-2 w-2 rounded-full bg-leafPrimary animate-bounce" />
                      <div
                        className="h-2 w-2 rounded-full bg-leafPrimary animate-bounce"
                        style={{ animationDelay: "0.15s" }}
                      />
                      <div
                        className="h-2 w-2 rounded-full bg-leafPrimary animate-bounce"
                        style={{ animationDelay: "0.3s" }}
                      />
                      <p className="text-xs text-slate-400">{t("rec_loading")}</p>
                    </div>
                  )}

                  {recError && !aiRecommendation && (
                    <p className="text-xs text-amber-300/90 bg-amber-500/10 p-2.5 rounded-lg border border-amber-500/20">
                      ⚠ {recError}
                    </p>
                  )}

                  {aiRecommendation ? (
                    <div className="whitespace-pre-wrap text-xs leading-relaxed text-slate-200 max-h-64 overflow-y-auto pr-1">
                      {aiRecommendation}
                    </div>
                  ) : (
                    !recLoading && (
                      <p className="text-xs leading-relaxed text-slate-200">
                        {result.suggestion || t("rec_empty_fallback")}
                      </p>
                    )
                  )}

                  {/* Standardized Chemical/Biological recommendation from backend */}
                  {result.treatment && (
                    <div className="mt-3 pt-3 border-t border-white/10 space-y-2">
                      <div className="text-[11px] text-slate-300">
                        <strong className="text-leafSecondary">Targeted Chemical: </strong>
                        {result.treatment.chemical}
                      </div>
                      <div className="text-[11px] text-slate-300">
                        <strong className="text-emerald-400">Organic / Bio: </strong>
                        {result.treatment.organic}
                      </div>
                      <div className="text-[11px] text-slate-400">
                        <strong className="text-amber-400">Prevention: </strong>
                        {result.treatment.preventive}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </motion.div>
          )}

          {/* ─────────────────────────────────────────────────────────────
              TAB 2: PEST DETECTION ADAPTER
          ───────────────────────────────────────────────────────────── */}
          {activeTab === "pest" && (
            <motion.div
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.2 }}
              className="space-y-6"
            >
              {loadingPest ? (
                <div className="glass-panel rounded-2xl p-8 text-center space-y-3">
                  <div className="h-6 w-6 border-2 border-leafSecondary border-t-transparent rounded-full animate-spin mx-auto" />
                  <p className="text-xs font-mono text-slate-400">Running Entomological Pest Detection Adapter…</p>
                </div>
              ) : pestData ? (
                <>
                  {/* Pest Overview Header Card */}
                  <div className="premium-card p-5 border border-leafSecondary/30">
                    <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="text-lg">🐛</span>
                          <h3 className="text-lg font-bold text-slate-100">{pestData.pest_name}</h3>
                          <span
                            className={`text-xs px-2.5 py-0.5 rounded-full border font-mono font-semibold ${pestRiskBadge(
                              pestData.risk_level || pestData.severity_rating
                            )}`}
                          >
                            {pestData.risk_level || pestData.severity_rating || "Low"} Risk
                          </span>
                        </div>
                        <p className="text-xs text-slate-400 mt-1">
                          Taxon:{" "}
                          <span className="text-slate-300 italic">
                            {pestData.scientific_name || "Phytophagous Species"}
                          </span>{" "}
                          • <span className="text-leafSecondary">{pestData.category || "Foliar Pest"}</span>
                        </p>
                      </div>

                      <div className="flex items-center gap-4">
                        <div className="text-right">
                          <p className="text-[10px] font-mono text-slate-400 uppercase">Infestation Level</p>
                          <p className="text-xl font-bold font-mono text-leafSecondary">
                            {Number(pestData.infestation_score ?? pestData.infestation_level ?? 25).toFixed(1)}%
                          </p>
                        </div>
                      </div>
                    </div>

                    {/* Infestation Gauge Bar */}
                    <div className="mt-4 space-y-1">
                      <div className="h-2 overflow-hidden rounded-full bg-white/10">
                        <motion.div
                          initial={{ scaleX: 0 }}
                          animate={{
                            scaleX: Number(pestData.infestation_score ?? pestData.infestation_level ?? 25) / 100,
                          }}
                          className="h-full origin-left rounded-full bg-gradient-to-r from-yellow-400 via-amber-500 to-red-500"
                        />
                      </div>
                    </div>

                    {/* Damage pattern & affected parts */}
                    {(pestData.damage_pattern || pestData.affected_parts) && (
                      <div className="mt-4 pt-3 border-t border-white/10 grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                        <div>
                          <span className="text-[10px] font-mono text-slate-400 uppercase block">Damage Symptoms</span>
                          <p className="text-slate-300 mt-0.5 leading-relaxed">{pestData.damage_pattern}</p>
                        </div>
                        <div>
                          <span className="text-[10px] font-mono text-slate-400 uppercase block">Affected Lamina Region</span>
                          <p className="text-slate-300 mt-0.5 leading-relaxed">{pestData.affected_parts}</p>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* 2-Column IPM Protocol (Biological vs Chemical) */}
                  <div className="grid gap-5 md:grid-cols-2">
                    {/* Biological Controls & Natural Predators */}
                    <div className="premium-card space-y-4">
                      <div className="flex items-center justify-between border-b border-white/10 pb-2">
                        <p className="text-xs tracking-[0.2em] text-emerald-400 font-mono uppercase">
                          Biological Control & Bio-Pesticides
                        </p>
                        <span className="text-[10px] text-emerald-400 font-mono">Organic IPM</span>
                      </div>

                      <div className="space-y-3">
                        {typeof pestData.biological_control === "string" ? (
                          <div className="rounded-lg bg-emerald-950/20 border border-emerald-500/20 p-3 text-xs text-slate-300 leading-relaxed">
                            <span className="text-emerald-400 mr-1.5">🐞</span>
                            {pestData.biological_control}
                          </div>
                        ) : (
                          <>
                            {pestData.biological_control?.beneficial_insects?.map((bio, idx) => (
                              <div
                                key={idx}
                                className="flex items-start gap-2 rounded-lg bg-emerald-950/20 border border-emerald-500/20 p-2 text-xs text-slate-300"
                              >
                                <span className="text-emerald-400 text-sm">🐞</span>
                                <span>{bio}</span>
                              </div>
                            ))}
                            {pestData.biological_control?.bio_pesticides?.map((spray, idx) => (
                              <div
                                key={idx}
                                className="flex items-start gap-2 rounded-lg bg-white/5 border border-white/10 p-2 text-xs text-slate-300"
                              >
                                <span className="text-leafPrimary text-sm">🌱</span>
                                <span>{spray}</span>
                              </div>
                            ))}
                          </>
                        )}
                      </div>
                    </div>

                    {/* Targeted Chemical Intervention */}
                    <div className="premium-card space-y-4">
                      <div className="flex items-center justify-between border-b border-white/10 pb-2">
                        <p className="text-xs tracking-[0.2em] text-leafSecondary font-mono uppercase">
                          Targeted Chemical Intervention
                        </p>
                        <span className="text-[10px] text-leafSecondary font-mono">Precision Dosage</span>
                      </div>

                      <div className="space-y-3">
                        {typeof pestData.chemical_control === "string" ? (
                          <div className="rounded-lg bg-black/30 border border-white/10 p-3 text-xs text-slate-200 leading-relaxed">
                            <span className="text-leafSecondary mr-1.5">🧪</span>
                            {pestData.chemical_control}
                          </div>
                        ) : (
                          <div className="space-y-2">
                            <div className="rounded-xl bg-black/30 border border-white/10 p-3 space-y-1">
                              <p className="text-[10px] font-mono text-slate-400 uppercase">Recommended Active</p>
                              <p className="text-xs font-bold text-slate-100">
                                {pestData.chemical_control?.recommended_active}
                              </p>
                            </div>
                            <div className="grid grid-cols-2 gap-3">
                              <div className="rounded-xl bg-black/30 border border-white/10 p-3">
                                <p className="text-[10px] font-mono text-slate-400 uppercase">Field Dosage</p>
                                <p className="text-xs font-semibold text-leafSecondary mt-0.5">
                                  {pestData.chemical_control?.dosage}
                                </p>
                              </div>
                              <div className="rounded-xl bg-black/30 border border-white/10 p-3">
                                <p className="text-[10px] font-mono text-slate-400 uppercase">PHI Safe Harvest</p>
                                <p className="text-xs font-semibold text-amber-300 mt-0.5">
                                  {pestData.chemical_control?.phi_days || 7} Days
                                </p>
                              </div>
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Cultural IPM Practices */}
                  {(pestData.cultural_management || pestData.cultural_ipm) && (
                    <div className="glass-panel rounded-2xl p-5 space-y-3 border border-white/10">
                      <p className="text-xs tracking-[0.2em] text-leafPrimary font-mono uppercase">
                        Cultural Field Management & Scouting Protocol
                      </p>
                      <div className="text-xs text-slate-300 leading-relaxed bg-white/5 p-3 rounded-xl border border-white/5">
                        {typeof pestData.cultural_management === "string"
                          ? pestData.cultural_management
                          : Array.isArray(pestData.cultural_ipm)
                          ? pestData.cultural_ipm.join(" • ")
                          : "Maintain routine field scouting with a 10x lens."}
                      </div>
                    </div>
                  )}
                </>
              ) : (
                <div className="glass-panel rounded-2xl p-8 text-center space-y-2">
                  <p className="text-xs text-slate-400">No pest diagnostic data available for this scan.</p>
                </div>
              )}
            </motion.div>
          )}

          {/* ─────────────────────────────────────────────────────────────
              TAB 3: NUTRITION DEFICIENCY ENGINE
          ───────────────────────────────────────────────────────────── */}
          {activeTab === "nutrition" && (
            <motion.div
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.2 }}
              className="space-y-6"
            >
              {loadingNutrition ? (
                <div className="glass-panel rounded-2xl p-8 text-center space-y-3">
                  <div className="h-6 w-6 border-2 border-emerald-400 border-t-transparent rounded-full animate-spin mx-auto" />
                  <p className="text-xs font-mono text-slate-400">Processing Multi-Spectral Nutrition Deficiency Engine…</p>
                </div>
              ) : nutritionData ? (
                <>
                  {/* Primary Nutrition Diagnosis Banner */}
                  <div className="premium-card p-5 border border-emerald-500/30">
                    <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="text-lg">🧪</span>
                          <h3 className="text-lg font-bold text-slate-100">
                            {nutritionData.primary_deficiency}
                          </h3>
                        </div>
                        <p className="text-xs text-slate-400 mt-1 font-mono">
                          Physiological Role: <span className="text-slate-200">{nutritionData.role || "Canopy Development"}</span>
                        </p>
                      </div>

                      <div className="flex items-center gap-4">
                        <div className="text-right">
                          <p className="text-[10px] font-mono text-slate-400 uppercase">Deficiency Severity</p>
                          <p className="text-xl font-bold font-mono text-amber-400">
                            {nutritionData.severity || "Moderate"}
                          </p>
                        </div>
                        <div className="text-right border-l border-white/10 pl-4">
                          <p className="text-[10px] font-mono text-slate-400 uppercase">Confidence</p>
                          <p className="text-xl font-bold font-mono text-slate-200">
                            {Number(nutritionData.confidence || 88).toFixed(1)}%
                          </p>
                        </div>
                      </div>
                    </div>

                    {/* Symptoms & Soil Factors */}
                    {(nutritionData.symptoms || nutritionData.soil_factors) && (
                      <div className="mt-4 pt-3 border-t border-white/10 grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                        <div>
                          <span className="text-[10px] font-mono text-slate-400 uppercase block">Diagnostic Biomarkers</span>
                          <p className="text-slate-300 mt-0.5 leading-relaxed">{nutritionData.symptoms}</p>
                        </div>
                        <div>
                          <span className="text-[10px] font-mono text-slate-400 uppercase block">Predisposing Soil Chemistry</span>
                          <p className="text-slate-300 mt-0.5 leading-relaxed">{nutritionData.soil_factors}</p>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Spectral Indices (Chlorosis, Scorch, Purpling, Vein Contrast) */}
                  {(nutritionData.spectral_indices || nutritionData.spectral_metrics) && (
                    <div className="glass-panel rounded-2xl p-5 space-y-3 border border-white/10">
                      <div className="flex items-center justify-between">
                        <p className="text-xs tracking-[0.2em] text-leafPrimary font-mono uppercase">
                          Spectral Canopy Telemetry
                        </p>
                        <span className="text-[10px] text-slate-400 font-mono">RGB Lamina Reflectance</span>
                      </div>

                      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                        {Object.entries(nutritionData.spectral_indices || nutritionData.spectral_metrics).map(
                          ([k, v]) => (
                            <div key={k} className="rounded-xl bg-black/30 border border-white/5 p-3 space-y-1">
                              <p className="text-[10px] font-mono text-slate-400 uppercase">
                                {k.replace(/_/g, " ")}
                              </p>
                              <p className="text-base font-bold font-mono text-leafSecondary">
                                {Number(v || 0).toFixed(1)}%
                              </p>
                              <div className="h-1 rounded-full bg-white/10 overflow-hidden">
                                <div
                                  className="h-full bg-leafSecondary rounded-full"
                                  style={{ width: `${Math.min(Number(v) * 2 || 20, 100)}%` }}
                                />
                              </div>
                            </div>
                          )
                        )}
                      </div>
                    </div>
                  )}

                  {/* Elemental Spectrum Bars */}
                  {nutritionData.elemental_spectrum && (
                    <div className="premium-card space-y-4">
                      <div className="flex items-center justify-between border-b border-white/10 pb-2">
                        <p className="text-xs tracking-[0.2em] text-leafPrimary font-mono uppercase">
                          7-Element Nutrient Balance Spectrum
                        </p>
                        <span className="text-[10px] text-slate-400 font-mono">N-P-K-Mg-Fe-Ca-Zn Profile</span>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                        {Object.entries(nutritionData.elemental_spectrum).map(([elem, val]) => {
                          const numVal = Number(val) || 75;
                          const isLow = numVal < 60;
                          return (
                            <div
                              key={elem}
                              className="rounded-xl bg-black/20 border border-white/5 p-3 space-y-1.5"
                            >
                              <div className="flex justify-between items-center text-xs">
                                <span className="font-semibold text-slate-200">{elem}</span>
                                <span
                                  className={`font-mono text-[10px] px-2 py-0.5 rounded-full border ${
                                    isLow
                                      ? "bg-red-500/20 text-red-400 border-red-500/30"
                                      : "bg-emerald-500/20 text-emerald-400 border-emerald-500/30"
                                  }`}
                                >
                                  {isLow ? "Deficient / Low" : "Optimal"} ({Math.round(numVal)}%)
                                </span>
                              </div>
                              <div className="h-1.5 rounded-full bg-white/10 overflow-hidden">
                                <div
                                  className={`h-full rounded-full ${
                                    isLow ? "bg-red-500" : "bg-emerald-400"
                                  }`}
                                  style={{ width: `${numVal}%` }}
                                />
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  )}

                  {/* 2-Column Actionable Prescription: Foliar Spray vs Soil Amendment */}
                  <div className="grid gap-5 md:grid-cols-2">
                    {/* Foliar Spray Correction */}
                    <div className="premium-card space-y-3 border border-leafSecondary/20">
                      <div className="flex items-center justify-between border-b border-white/10 pb-2">
                        <p className="text-xs tracking-[0.2em] text-leafSecondary font-mono uppercase">
                          Rapid Foliar Spray Recipe
                        </p>
                        <span className="text-[10px] text-leafSecondary font-mono">Immediate Uptake</span>
                      </div>

                      <div className="rounded-lg bg-black/30 border border-white/10 p-3 text-xs text-slate-200 leading-relaxed">
                        <span className="text-leafSecondary mr-1.5 font-bold">🌿 Application:</span>
                        {typeof nutritionData.foliar_correction === "string"
                          ? nutritionData.foliar_correction
                          : nutritionData.foliar_spray_recipe?.fertilizer ||
                            "Apply balanced water-soluble micronutrient foliar spray."}
                      </div>
                    </div>

                    {/* Soil Amendment Strategy */}
                    <div className="premium-card space-y-3 border border-emerald-500/20">
                      <div className="flex items-center justify-between border-b border-white/10 pb-2">
                        <p className="text-xs tracking-[0.2em] text-emerald-400 font-mono uppercase">
                          Soil Amendment & Root Zone Strategy
                        </p>
                        <span className="text-[10px] text-emerald-400 font-mono">Long-Term Fertility</span>
                      </div>

                      <div className="rounded-lg bg-black/30 border border-white/10 p-3 text-xs text-slate-200 leading-relaxed">
                        <span className="text-emerald-400 mr-1.5 font-bold">🌱 Soil Management:</span>
                        {typeof nutritionData.soil_amendment === "string"
                          ? nutritionData.soil_amendment
                          : nutritionData.soil_amendment?.recommendation ||
                            "Apply well-composted organic manure to enhance cation exchange capacity."}
                      </div>
                    </div>
                  </div>
                </>
              ) : (
                <div className="glass-panel rounded-2xl p-8 text-center space-y-2">
                  <p className="text-xs text-slate-400">No nutritional analysis data available for this scan.</p>
                </div>
              )}
            </motion.div>
          )}
        </>
      )}
    </section>
  );
}

export default Results;
