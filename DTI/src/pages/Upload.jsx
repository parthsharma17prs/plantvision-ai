import { useMemo, useState } from "react";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import Button from "../components/Button";
import Loader from "../components/Loader";

function Upload() {
  const [preview, setPreview] = useState("");
  const [isScanning, setIsScanning] = useState(false);
  const [isDragActive, setIsDragActive] = useState(false);
  const navigate = useNavigate();

  const dropText = useMemo(() => {
    if (preview) return "Image loaded. Ready for AI scanning.";
    if (isDragActive) return "Drop image to begin analysis";
    return "Drag and drop or tap to select a leaf image";
  }, [preview, isDragActive]);

  const processFile = (file) => {
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => setPreview(reader.result);
    reader.readAsDataURL(file);
  };

  const handleDrop = (event) => {
    event.preventDefault();
    setIsDragActive(false);
    processFile(event.dataTransfer.files?.[0]);
  };

  const handleScan = () => {
    if (!preview) return;
    setIsScanning(true);

    const dummy = {
      disease: "Early Blight",
      severity: 78,
      suggestion: "Apply copper-based fungicide every 7 days and isolate affected crop clusters.",
      boxes: [
        "top-[20%] left-[16%] w-[28%] h-[22%]",
        "top-[54%] left-[52%] w-[26%] h-[20%]",
      ],
    };

    setTimeout(() => {
      localStorage.setItem("leafx-image", preview);
      localStorage.setItem("leafx-result", JSON.stringify(dummy));
      navigate("/results");
    }, 1800);
  };

  return (
    <section className="page-shell">
      <div className="grid gap-6 lg:grid-cols-[244px_1fr]">
        <Sidebar />

        <div className="space-y-6">
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">Upload for AI Scan</h2>

          <label
            onDragEnter={(event) => {
              event.preventDefault();
              setIsDragActive(true);
            }}
            onDragOver={(event) => event.preventDefault()}
            onDragLeave={() => setIsDragActive(false)}
            onDrop={handleDrop}
            className={`glass-panel block cursor-pointer rounded-2xl border-2 border-dashed p-8 text-center transition ${
              isDragActive ? "border-leafSecondary shadow-glowSecondary" : "border-white/20 hover:border-leafPrimary/55"
            }`}
          >
            <input
              type="file"
              accept="image/*"
              className="hidden"
              onChange={(event) => processFile(event.target.files?.[0])}
            />
            <p className="text-base font-medium text-textSoft">{dropText}</p>
            <p className="mt-2 text-sm text-slate-400">PNG/JPG up to 10MB</p>
          </label>

          {preview && (
            <div className="glass-panel relative overflow-hidden rounded-2xl p-4">
              <img src={preview} alt="Leaf preview" className="max-h-[360px] w-full rounded-xl object-cover" />
              {isScanning && (
                <motion.div
                  animate={{ y: ["-10%", "108%"] }}
                  transition={{ duration: 1.2, repeat: Infinity, ease: "linear" }}
                  className="pointer-events-none absolute left-4 right-4 h-8 bg-gradient-to-b from-transparent via-leafSecondary/40 to-transparent blur-sm"
                />
              )}
            </div>
          )}

          {isScanning ? (
            <Loader text="Running visual inference and segmenting infected regions..." />
          ) : (
            <Button onClick={handleScan} disabled={!preview} className="disabled:cursor-not-allowed disabled:opacity-50">
              Scan with AI
            </Button>
          )}
        </div>
      </div>
    </section>
  );
}

export default Upload;
