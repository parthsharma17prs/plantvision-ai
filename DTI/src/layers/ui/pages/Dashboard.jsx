import { useState, useEffect, useCallback, useRef } from "react";
import { motion } from "framer-motion";
import {
  getPredictionHistory,
  getDriveStatus,
  syncDriveNow,
  getLatestResult
} from "../../services/api/predictionApi";

// ── Donut Chart (SVG, no external lib) ──────────────────────────────────────
function DonutChart({ healthy, diseased }) {
  const total = healthy + diseased;
  if (total === 0) {
    return (
      <div className="flex h-36 items-center justify-center">
        <p className="text-slate-500 text-xs">No data yet</p>
      </div>
    );
  }
  const r = 50;
  const cx = 60;
  const cy = 60;
  const circ = 2 * Math.PI * r;
  const healthyPct = healthy / total;
  const diseasedPct = diseased / total;
  const healthyArc = healthyPct * circ;
  const diseasedArc = diseasedPct * circ;

  return (
    <div className="flex items-center gap-6">
      <svg width="120" height="120" viewBox="0 0 120 120">
        {/* Diseased segment */}
        <circle cx={cx} cy={cy} r={r} fill="none" stroke="#ef4444" strokeWidth="16"
          strokeDasharray={`${diseasedArc} ${circ}`}
          strokeDashoffset={0}
          transform={`rotate(-90 ${cx} ${cy})`}
          strokeLinecap="butt"
        />
        {/* Healthy segment */}
        <circle cx={cx} cy={cy} r={r} fill="none" stroke="#10b981" strokeWidth="16"
          strokeDasharray={`${healthyArc} ${circ}`}
          strokeDashoffset={-diseasedArc}
          transform={`rotate(-90 ${cx} ${cy})`}
          strokeLinecap="butt"
        />
        {/* Center text */}
        <text x={cx} y={cy - 4} textAnchor="middle" fill="#d1fae5" fontSize="14" fontWeight="bold">
          {total}
        </text>
        <text x={cx} y={cy + 12} textAnchor="middle" fill="#64748b" fontSize="9">
          total
        </text>
      </svg>
      <div className="space-y-2">
        <div className="flex items-center gap-2">
          <div className="h-3 w-3 rounded-full bg-emerald-500" />
          <span className="text-xs text-slate-300">Healthy <strong className="text-emerald-400">{healthy}</strong></span>
        </div>
        <div className="flex items-center gap-2">
          <div className="h-3 w-3 rounded-full bg-red-500" />
          <span className="text-xs text-slate-300">Diseased <strong className="text-red-400">{diseased}</strong></span>
        </div>
        <p className="text-xs text-slate-500">
          Disease rate: <span className="text-amber-400">{total > 0 ? ((diseased / total) * 100).toFixed(1) : 0}%</span>
        </p>
      </div>
    </div>
  );
}

// ── Line Chart (SVG, confidence over time) ──────────────────────────────────
function ConfidenceChart({ history }) {
  if (!history || history.length === 0) {
    return (
      <div className="flex h-32 items-center justify-center">
        <p className="text-slate-500 text-xs">No scan history yet — data will chart here automatically</p>
      </div>
    );
  }

  const data = [...history].reverse().slice(-20);
  const W = 400;
  const H = 100;
  const pad = { top: 10, right: 10, bottom: 20, left: 30 };
  const innerW = W - pad.left - pad.right;
  const innerH = H - pad.top - pad.bottom;

  const minConf = Math.max(0, Math.min(...data.map((d) => d.confidence || 0)) - 5);
  const maxConf = Math.min(100, Math.max(...data.map((d) => d.confidence || 0)) + 5);
  const range = maxConf - minConf || 10;

  const points = data.map((d, i) => {
    const x = pad.left + (i / Math.max(data.length - 1, 1)) * innerW;
    const y = pad.top + ((maxConf - (d.confidence || 0)) / range) * innerH;
    return `${x},${y}`;
  });

  const polyline = points.join(" ");
  const areaPath = `M${pad.left},${pad.top + innerH} L${points.join(" L")} L${pad.left + innerW},${pad.top + innerH} Z`;

  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full h-28" preserveAspectRatio="none">
      <defs>
        <linearGradient id="confGrad" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#10b981" stopOpacity="0.3" />
          <stop offset="100%" stopColor="#10b981" stopOpacity="0.02" />
        </linearGradient>
      </defs>
      <path d={areaPath} fill="url(#confGrad)" />
      <polyline points={polyline} fill="none" stroke="#10b981" strokeWidth="2" strokeLinejoin="round" />
      {points.map((p, i) => {
        const [x, y] = p.split(",").map(Number);
        return <circle key={i} cx={x} cy={y} r="3" fill="#34d399" />;
      })}
      <text x={pad.left - 2} y={pad.top + 4} textAnchor="end" fill="#64748b" fontSize="8">{Math.round(maxConf)}%</text>
      <text x={pad.left - 2} y={pad.top + innerH} textAnchor="end" fill="#64748b" fontSize="8">{Math.round(minConf)}%</text>
    </svg>
  );
}

// ── Metric Card ─────────────────────────────────────────────────────────────
function MetricCard({ label, value, sub, accent = "text-leafSecondary" }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      className="premium-card text-center"
    >
      <p className="text-xs tracking-[0.18em] text-slate-400 uppercase">{label}</p>
      <p className={`mt-2 text-3xl font-extrabold ${accent}`}>{value}</p>
      {sub && <p className="mt-1 text-xs text-slate-500">{sub}</p>}
    </motion.div>
  );
}

// ── Status Pill ─────────────────────────────────────────────────────────────
function StatusPill({ online }) {
  return (
    <span className={`flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-semibold ${
      online ? "bg-emerald-900/50 text-emerald-300" : "bg-red-900/50 text-red-300"
    }`}>
      <span className={`h-2 w-2 rounded-full ${online ? "bg-emerald-400 animate-pulse" : "bg-red-400"}`} />
      {online ? "ONLINE" : "OFFLINE"}
    </span>
  );
}

// ── Main Dashboard Component ────────────────────────────────────────────────
function Dashboard() {
  const [history, setHistory] = useState([]);
  const [health, setHealth] = useState(null);
  const [driveStatus, setDriveStatus] = useState(null);
  const [latestResult, setLatestResult] = useState(null);
  const [syncingDrive, setSyncingDrive] = useState(false);
  const [loading, setLoading] = useState(true);
  const pollRef = useRef(null);

  const computeStats = useCallback((hist) => {
    const total = hist.length;
    const healthy = hist.filter((h) =>
      (h.disease || "").toLowerCase().includes("healthy")
    ).length;
    const diseased = total - healthy;
    const avgConf = total > 0
      ? hist.reduce((s, h) => s + (h.confidence || 0), 0) / total
      : 0;
    const highConf = hist.filter((h) => (h.confidence || 0) >= 90).length;
    const medConf = hist.filter((h) => (h.confidence || 0) >= 50 && (h.confidence || 0) < 90).length;
    const lowConf = hist.filter((h) => (h.confidence || 0) < 50).length;
    return { total, healthy, diseased, avgConf, highConf, medConf, lowConf };
  }, []);

  const loadData = useCallback(async () => {
    try {
      const [hist, healthData, drvData, latest] = await Promise.all([
        getPredictionHistory(),
        fetch("/api/health").then((r) => r.json()).catch(() => null),
        getDriveStatus().catch(() => null),
        getLatestResult().catch(() => null),
      ]);
      setHistory(hist || []);
      setHealth(healthData);
      setDriveStatus(drvData);
      if (latest && latest.disease) {
        setLatestResult(latest);
      } else if (hist && hist.length > 0) {
        setLatestResult(hist[0]);
      }
    } catch (e) {
      console.error("Dashboard load error:", e);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
    // Continuous live poll every 5 seconds for Drive and real-time updates
    pollRef.current = setInterval(loadData, 5000);
    return () => clearInterval(pollRef.current);
  }, [loadData]);

  // Manual Trigger for Google Drive Ingestion
  const handleDriveSync = async () => {
    setSyncingDrive(true);
    try {
      const res = await syncDriveNow();
      if (res?.synced && res?.result) {
        setLatestResult(res.result);
      }
      await loadData();
    } catch (e) {
      console.error("Drive sync error:", e);
    } finally {
      setSyncingDrive(false);
    }
  };

  const stats = computeStats(history);
  const online = health?.status === "ok";
  const modelName = health?.weights || "Not loaded";
  const modelTrained = health?.model_trained !== false;

  if (loading) {
    return (
      <section className="page-shell flex min-h-[60vh] items-center justify-center">
        <div className="text-center space-y-4">
          <div className="flex justify-center gap-2">
            {[0, 1, 2].map((i) => (
              <div key={i} className="h-3 w-3 rounded-full bg-leafPrimary animate-bounce" style={{ animationDelay: `${i * 0.15}s` }} />
            ))}
          </div>
          <p className="text-slate-400 text-sm">Loading crop diagnostics &amp; live telemetry…</p>
        </div>
      </section>
    );
  }

  return (
    <section className="page-shell space-y-6">
      {/* ── Header ── */}
      <div className="glass-panel rounded-2xl p-6">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="text-xs tracking-[0.22em] text-leafPrimary">PLANTVISION AI</p>
            <h1 className="mt-1 text-2xl font-extrabold tracking-tight">Crop Health &amp; Agribot Dashboard</h1>
            <p className="mt-1 text-sm text-slate-400">Continuous Google Drive Ingestion → YOLO Diagnostics → Live Telemetry</p>
          </div>
          <div className="flex flex-wrap items-center gap-3">
            <StatusPill online={online} />
            <div className="glass-panel rounded-xl px-3 py-2 text-xs">
              <span className="text-slate-400">Model: </span>
              <span className="text-leafSecondary font-semibold">{modelName}</span>
              {!modelTrained && (
                <span className="ml-2 rounded-full bg-amber-900/50 px-2 py-0.5 text-amber-400 text-[10px]">
                  Base YOLO
                </span>
              )}
            </div>
            <button
              onClick={handleDriveSync}
              disabled={syncingDrive}
              className="rounded-xl border border-leafPrimary/40 bg-leafPrimary/15 px-3.5 py-2 text-xs font-semibold text-leafPrimary hover:bg-leafPrimary/25 transition disabled:opacity-50 flex items-center gap-1.5"
            >
              {syncingDrive ? "⏳ Syncing…" : "🔄 Sync Drive Now"}
            </button>
            <button
              onClick={loadData}
              className="rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-xs text-slate-300 hover:bg-white/10 transition"
            >
              ↻ Refresh
            </button>
          </div>
        </div>
      </div>

      {/* ── Google Drive Live Stream Panel ── */}
      <div className="glass-panel rounded-2xl p-6 border-leafPrimary/20 bg-gradient-to-br from-emerald-950/30 to-slate-900/50">
        <div className="flex flex-wrap items-center justify-between gap-4 mb-4">
          <div className="flex items-center gap-3">
            <span className="flex h-3 w-3 relative">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
            </span>
            <div>
              <h2 className="text-base font-bold text-slate-100 flex items-center gap-2">
                Google Drive Ingestion Pipeline
                <span className="text-xs px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 font-mono">
                  {driveStatus?.status || "monitoring"}
                </span>
              </h2>
              <p className="text-xs text-slate-400 mt-0.5">
                Monitoring Folder ID: <span className="font-mono text-slate-300">{driveStatus?.folder_id || "1nRLc9j0Fb3XoYu1WzeeknM1acwdzAndE"}</span> (Interval: {driveStatus?.polling_interval_sec || 5}s)
              </p>
            </div>
          </div>
          <div className="flex items-center gap-4 text-xs">
            <div className="text-right">
              <p className="text-slate-400">Total Ingested from Drive</p>
              <p className="text-base font-extrabold text-leafSecondary">{driveStatus?.total_processed || 0} images</p>
            </div>
            <div className="text-right">
              <p className="text-slate-400">Last Synced File</p>
              <p className="text-xs font-mono text-slate-200 truncate max-w-[150px]">{driveStatus?.last_processed_filename || "Waiting for upload"}</p>
            </div>
          </div>
        </div>

        {/* Live Diagnosis Banner from Latest Drive Ingestion or Scan */}
        {latestResult && latestResult.disease ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-5 items-center rounded-xl bg-black/40 border border-white/10 p-4">
            {/* Annotated Image Viewfinder */}
            <div className="relative rounded-lg overflow-hidden border border-emerald-500/30 bg-black/60 flex items-center justify-center min-h-[180px] max-h-[220px]">
              {latestResult.annotatedImage ? (
                <img
                  src={latestResult.annotatedImage}
                  alt="Annotated Leaf"
                  className="w-full h-full object-contain"
                />
              ) : (
                <div className="text-center p-4 text-xs text-slate-400">
                  <span>🍃 Live Leaf Feed</span>
                </div>
              )}
              <span className="absolute top-2 left-2 bg-black/70 backdrop-blur text-emerald-400 text-[10px] font-mono px-2 py-0.5 rounded border border-emerald-500/30">
                {latestResult.source === "google_drive" ? "DRIVE FEED" : "DIAGNOSTIC SCAN"}
              </span>
            </div>

            {/* Disease Metrics */}
            <div className="space-y-3">
              <div>
                <p className="text-[11px] uppercase tracking-wider text-slate-400">Diagnosed Condition</p>
                <h3 className={`text-2xl font-black ${
                  (latestResult.disease || "").toLowerCase().includes("healthy") ? "text-emerald-400" : "text-rose-400"
                }`}>
                  {latestResult.disease}
                </h3>
              </div>
              <div className="grid grid-cols-3 gap-2 text-center text-xs">
                <div className="bg-white/5 rounded-lg p-2">
                  <p className="text-slate-400 text-[10px]">Confidence</p>
                  <p className="font-bold text-leafSecondary text-sm">{Number(latestResult.confidence || 0).toFixed(1)}%</p>
                </div>
                <div className="bg-white/5 rounded-lg p-2">
                  <p className="text-slate-400 text-[10px]">Severity</p>
                  <p className="font-bold text-amber-400 text-sm">{Number(latestResult.severity || 0).toFixed(1)}%</p>
                </div>
                <div className="bg-white/5 rounded-lg p-2">
                  <p className="text-slate-400 text-[10px]">Health</p>
                  <p className="font-bold text-emerald-400 text-sm">{Number(latestResult.plantHealth || 0).toFixed(1)}%</p>
                </div>
              </div>
              <p className="text-[11px] text-slate-400">
                File: <span className="font-mono text-slate-300">{latestResult.filename || "scan.jpg"}</span> • {latestResult.timestamp ? new Date(latestResult.timestamp).toLocaleTimeString() : "Just now"}
              </p>
            </div>

            {/* Treatment Recommendation */}
            <div className="bg-white/5 rounded-xl p-3.5 border border-white/5 text-xs space-y-2">
              <p className="text-[10px] uppercase font-bold tracking-wider text-leafPrimary">🌾 Agricultural Treatment Advice</p>
              <p className="text-slate-200 leading-relaxed text-xs">
                {latestResult.suggestion || "Continue regular irrigation and nutrient feeding. Inspect leaves weekly."}
              </p>
              <div className="pt-1 flex gap-2">
                <a href="/results" className="text-[11px] font-semibold text-leafSecondary hover:underline">
                  View Full Diagnosis &amp; Gemini Advice →
                </a>
              </div>
            </div>
          </div>
        ) : (
          <div className="text-center py-6 border border-dashed border-white/10 rounded-xl">
            <p className="text-slate-400 text-xs">Drive poller is actively listening. When a leaf image arrives in Google Drive, it will automatically run through the YOLO model and update here.</p>
          </div>
        )}
      </div>

      {/* ── Metrics Row ── */}
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <MetricCard
          label="Total Analyzed"
          value={stats.total}
          sub="cumulative leaf scans"
          accent="text-leafSecondary"
        />
        <MetricCard
          label="Healthy Crops"
          value={stats.healthy}
          sub={`${stats.total > 0 ? ((stats.healthy / stats.total) * 100).toFixed(1) : 0}% of total`}
          accent="text-emerald-400"
        />
        <MetricCard
          label="Infections Detected"
          value={stats.diseased}
          sub={`${stats.total > 0 ? ((stats.diseased / stats.total) * 100).toFixed(1) : 0}% infection rate`}
          accent="text-red-400"
        />
        <MetricCard
          label="Avg Model Confidence"
          value={`${stats.avgConf.toFixed(1)}%`}
          sub="across all detections"
          accent={stats.avgConf >= 75 ? "text-emerald-400" : stats.avgConf >= 50 ? "text-amber-400" : "text-red-400"}
        />
      </div>

      {/* ── Charts Grid ── */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Confidence Over Time */}
        <div className="premium-card lg:col-span-2 space-y-3">
          <div className="flex items-center justify-between">
            <p className="text-xs tracking-[0.2em] text-leafPrimary">CONFIDENCE TREND OVER TIME</p>
            <p className="text-xs text-slate-500">Last {Math.min(history.length, 20)} predictions</p>
          </div>
          <ConfidenceChart history={history} />
        </div>

        {/* Healthy vs Diseased Donut */}
        <div className="premium-card space-y-3">
          <p className="text-xs tracking-[0.2em] text-leafPrimary">HEALTHY vs DISEASED RATIO</p>
          <DonutChart healthy={stats.healthy} diseased={stats.diseased} />
          <div className="border-t border-white/10 pt-3 space-y-2">
            <p className="text-xs text-slate-500">Confidence Distribution:</p>
            <div className="flex items-center gap-2 text-xs">
              <div className="h-2 w-2 rounded-full bg-emerald-500" />
              <span className="text-slate-400">High (&gt;90%)</span>
              <span className="ml-auto text-emerald-400 font-semibold">{stats.highConf}</span>
            </div>
            <div className="flex items-center gap-2 text-xs">
              <div className="h-2 w-2 rounded-full bg-amber-500" />
              <span className="text-slate-400">Medium (50–90%)</span>
              <span className="ml-auto text-amber-400 font-semibold">{stats.medConf}</span>
            </div>
            <div className="flex items-center gap-2 text-xs">
              <div className="h-2 w-2 rounded-full bg-red-500" />
              <span className="text-slate-400">Low (&lt;50%)</span>
              <span className="ml-auto text-red-400 font-semibold">{stats.lowConf}</span>
            </div>
          </div>
        </div>
      </div>

      {/* ── Recent History Log ── */}
      <div className="premium-card space-y-3">
        <div className="flex items-center justify-between">
          <p className="text-xs tracking-[0.2em] text-leafPrimary">DIAGNOSTIC HISTORY LOG</p>
          <a
            href="/api/history/export"
            className="text-xs text-leafSecondary hover:underline"
            download
          >
            📥 Export CSV
          </a>
        </div>
        <div className="space-y-2 max-h-72 overflow-y-auto pr-1">
          {history.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-8 gap-2">
              <p className="text-slate-500 text-xs">No scan history recorded yet.</p>
              <a href="/scan" className="text-xs text-leafPrimary hover:underline">Run manual scan →</a>
            </div>
          ) : (
            history.map((item, i) => {
              const isHealthy = (item.disease || "").toLowerCase().includes("healthy");
              const conf = Number(item.confidence || 0);
              return (
                <motion.div
                  key={item.id || i}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.02 }}
                  className="flex items-center gap-3 rounded-xl bg-white/5 px-4 py-2.5"
                >
                  <span className={`h-2.5 w-2.5 flex-shrink-0 rounded-full ${isHealthy ? "bg-emerald-400" : "bg-red-400"}`} />
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm font-semibold text-slate-200">{item.disease}</p>
                    <p className="text-xs text-slate-400 truncate">
                      {item.filename ? `${item.filename} • ` : ""}
                      {item.source === "google_drive" ? "Google Drive • " : ""}
                      {item.createdAt ? new Date(item.createdAt).toLocaleString() : "—"}
                    </p>
                  </div>
                  <div className="text-right flex-shrink-0">
                    <p className={`text-sm font-bold ${
                      conf >= 90 ? "text-emerald-400" : conf >= 50 ? "text-amber-400" : "text-red-400"
                    }`}>
                      {conf.toFixed(1)}%
                    </p>
                    <p className={`text-xs font-medium ${isHealthy ? "text-emerald-500" : "text-rose-400"}`}>
                      {isHealthy ? "Healthy" : "Infected"}
                    </p>
                  </div>
                </motion.div>
              );
            })
          )}
        </div>
      </div>
    </section>
  );
}

export default Dashboard;
