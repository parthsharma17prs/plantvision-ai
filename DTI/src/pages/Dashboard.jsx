import { motion } from "framer-motion";
import Card from "../components/Card";
import Sidebar from "../components/Sidebar";

function Dashboard() {
  return (
    <section className="page-shell">
      <div className="grid gap-6 lg:grid-cols-[244px_1fr]">
        <Sidebar />

        <div className="space-y-7">
          <div className="glass-panel rounded-2xl p-6">
            <p className="text-xs tracking-[0.24em] text-leafPrimary">AI CONTROL CENTER</p>
            <h2 className="mt-3 text-3xl font-bold tracking-tight sm:text-4xl">Operations Dashboard</h2>
            <p className="mt-2 text-sm text-slate-300">Live scan telemetry, model confidence trends, and recent field alerts.</p>
          </div>

          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
            <Card title="Total Scans" value="1,284" subtitle="Across all monitored farms this month" accent="green" />
            <Card title="Model Accuracy" value="97.8%" subtitle="Stable confidence across latest validation batch" />
            <Card title="Recent Alerts" value="43" subtitle="Potential disease spikes detected in 24h" />
          </div>

          <div className="glass-panel rounded-2xl p-6">
            <h3 className="text-lg font-semibold tracking-wide">Activity Pulse</h3>
            <div className="mt-5 grid gap-3 sm:grid-cols-3">
              {[65, 78, 52].map((val, idx) => (
                <div key={idx} className="rounded-xl border border-white/10 bg-white/[0.03] p-4">
                  <p className="text-xs uppercase tracking-[0.18em] text-slate-400">Zone {idx + 1}</p>
                  <div className="mt-3 h-2 rounded-full bg-white/10">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${val}%` }}
                      transition={{ duration: 0.8, delay: idx * 0.1 }}
                      className="h-full rounded-full bg-gradient-to-r from-leafPrimary to-leafSecondary"
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

export default Dashboard;
