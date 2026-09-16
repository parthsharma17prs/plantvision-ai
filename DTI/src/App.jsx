import { Routes, Route } from "react-router-dom";
import { AnimatePresence } from "framer-motion";
import Navbar from "./layers/ui/components/Navbar";
import BottomNav from "./layers/ui/components/BottomNav";
import PageTransition from "./layers/ui/components/PageTransition";
import FloatingChatbot from "./layers/ai/components/FloatingChatbot";
import Landing from "./layers/ui/pages/Landing";
import Login from "./layers/ui/pages/Login";
import Scan from "./layers/ui/pages/Scan";
import Results from "./layers/ui/pages/Results";
import Weather from "./layers/ui/pages/Weather";
import Dashboard from "./layers/ui/pages/Dashboard";

function App() {
  return (
    <div className="relative min-h-screen overflow-x-hidden bg-brand text-textSoft">
      <div className="pointer-events-none fixed inset-0 bg-[radial-gradient(circle_at_14%_14%,rgba(0,255,156,0.1),transparent_36%),radial-gradient(circle_at_85%_16%,rgba(0,207,255,0.1),transparent_40%)]" />
      <div className="pointer-events-none fixed inset-0 mesh-bg opacity-15" />
      <div className="pointer-events-none fixed inset-0 mesh-bg opacity-10" />

      <Navbar />
      <AnimatePresence mode="wait">
        <PageTransition>
          <Routes>
            <Route path="/" element={<Landing />} />
            <Route path="/login" element={<Login />} />
            <Route path="/scan" element={<Scan />} />
            <Route path="/results" element={<Results />} />
            <Route path="/weather" element={<Weather />} />
            <Route path="/dashboard" element={<Dashboard />} />
          </Routes>
        </PageTransition>
      </AnimatePresence>
      <BottomNav />
      <FloatingChatbot />
    </div>
  );
}

export default App;
