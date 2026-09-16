import { useRef, useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import Button from "../components/Button";
import ScanOverlay from "../../ai/components/ScanOverlay";
import { runPrediction } from "../../services/api/predictionApi";

function Scan() {
  const { t } = useTranslation();
  const [image, setImage] = useState("");
  const [scanning, setScanning] = useState(false);
  const [cameraOn, setCameraOn] = useState(false);
  const [error, setError] = useState("");
  const [modelInfo, setModelInfo] = useState(null);
  const videoRef = useRef(null);
  const navigate = useNavigate();

  // Fetch model info on mount
  useEffect(() => {
    fetch("/api/health")
      .then((r) => r.json())
      .then((d) => setModelInfo(d))
      .catch(() => setModelInfo(null));
  }, []);

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        setCameraOn(true);
      }
    } catch {
      setCameraOn(false);
      setError("Camera access denied. Please allow camera permission or upload an image.");
    }
  };

  const captureFrame = () => {
    if (!videoRef.current) return;
    const canvas = document.createElement("canvas");
    canvas.width = videoRef.current.videoWidth || 1280;
    canvas.height = videoRef.current.videoHeight || 720;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    ctx.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);
    setImage(canvas.toDataURL("image/png"));
  };

  const runScan = () => {
    if (!image) return;
    setError("");
    setScanning(true);
    runPrediction(image)
      .then((prediction) => {
        localStorage.setItem("plantvision-image", image);
        localStorage.setItem("plantvision-result", JSON.stringify(prediction));
        // Notify dashboard of new prediction
        window.dispatchEvent(new CustomEvent("plantvision-new-scan", { detail: prediction }));
        navigate("/results");
      })
      .catch((err) => {
        setError(err?.message || "Failed to run prediction. Is the backend running?");
      })
      .finally(() => {
        setScanning(false);
      });
  };

  return (
    <section className="page-shell space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-3xl font-bold">{t("scan_title")}</h2>
        {modelInfo && (
          <div className="flex items-center gap-2 text-xs">
            <span className={`h-2 w-2 rounded-full ${modelInfo.status === "ok" ? "bg-leafPrimary animate-pulse" : "bg-red-400"}`} />
            <span className="text-slate-400">
              Model: <span className="text-leafSecondary">{modelInfo.weights || "unknown"}</span>
            </span>
          </div>
        )}
      </div>

      <div className="glass-panel rounded-2xl p-4">
        <div className="relative overflow-hidden rounded-xl border border-leafPrimary/40 bg-black/30">
          {!image ? (
            <div className="aspect-video flex items-center justify-center">
              <video ref={videoRef} autoPlay playsInline className="h-full w-full object-cover" />
              {!cameraOn && (
                <div className="absolute inset-0 flex flex-col items-center justify-center gap-3">
                  <div className="text-5xl opacity-30">🌿</div>
                  <p className="text-slate-400 text-sm">Enable camera or upload a leaf image</p>
                </div>
              )}
            </div>
          ) : (
            <div className="relative">
              <img src={image} alt={t("captured_leaf_alt")} className="aspect-video w-full object-cover" />
              <button
                onClick={() => setImage("")}
                className="absolute top-2 right-2 rounded-full bg-black/60 px-3 py-1 text-xs text-slate-300 hover:bg-black/80 transition"
              >
                ✕ Clear
              </button>
            </div>
          )}
          {scanning && <ScanOverlay />}
        </div>
      </div>

      <div className="flex flex-wrap gap-3">
        <Button onClick={startCamera}>{t("enable_camera")}</Button>
        {cameraOn && <Button variant="secondary" onClick={captureFrame}>{t("capture_frame")}</Button>}
        <label className="cursor-pointer rounded-full border border-white/20 bg-white/[0.04] px-5 py-3 text-sm text-slate-200 hover:bg-white/[0.08] transition">
          {t("upload_image")}
          <input
            type="file"
            accept="image/*"
            className="hidden"
            onChange={(event) => {
              const file = event.target.files?.[0];
              if (!file) return;
              const reader = new FileReader();
              reader.onload = () => setImage(String(reader.result));
              reader.readAsDataURL(file);
            }}
          />
        </label>
        <Button
          onClick={runScan}
          className="disabled:opacity-60"
          disabled={!image || scanning}
        >
          {scanning ? "Scanning…" : t("scan_now")}
        </Button>
      </div>

      {error && (
        <div className="glass-panel rounded-xl p-4 border-rose-500/30">
          <p className="text-sm text-rose-400">⚠ {error}</p>
        </div>
      )}

      {/* Tri-Engine Diagnostic Pipeline Architecture */}
      <div className="glass-panel rounded-2xl p-6 space-y-4 border border-leafPrimary/20">
        <div className="flex items-center justify-between border-b border-white/10 pb-3">
          <p className="text-xs tracking-[0.2em] text-leafPrimary font-mono uppercase">
            Tri-Engine Multi-Spectral Diagnostic Pipeline
          </p>
          <span className="text-[11px] font-mono text-leafSecondary bg-leafSecondary/10 px-2 py-0.5 rounded-full border border-leafSecondary/30">
            v3.2 Active
          </span>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-1">
          <div className="rounded-xl bg-black/20 p-3.5 border border-white/5 space-y-1.5">
            <div className="flex items-center gap-2">
              <span className="text-lg">🔬</span>
              <span className="text-xs font-semibold text-slate-200">1. YOLOv8 Pathology</span>
            </div>
            <p className="text-[11px] text-slate-400 leading-relaxed">
              Spatial localization of fungal, bacterial, and viral foliar lesions with bounding boxes and severity percentages.
            </p>
          </div>
          <div className="rounded-xl bg-black/20 p-3.5 border border-white/5 space-y-1.5">
            <div className="flex items-center gap-2">
              <span className="text-lg">🐛</span>
              <span className="text-xs font-semibold text-leafSecondary">2. Pest Detection Adapter</span>
            </div>
            <p className="text-[11px] text-slate-400 leading-relaxed">
              Diagnoses mites, aphids, thrips, and leafminers with biocontrol predators, organic neem IPM, and exact spray dosages.
            </p>
          </div>
          <div className="rounded-xl bg-black/20 p-3.5 border border-white/5 space-y-1.5">
            <div className="flex items-center gap-2">
              <span className="text-lg">🧪</span>
              <span className="text-xs font-semibold text-emerald-400">3. Nutrition Deficiency Engine</span>
            </div>
            <p className="text-[11px] text-slate-400 leading-relaxed">
              Multi-spectral analysis of chlorosis & necrosis mapping N-P-K-Mg-Fe-Ca-Zn balances with foliar spray recipes.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}

export default Scan;
