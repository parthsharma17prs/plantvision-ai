import { useState, useRef, useEffect } from "react";
import { motion } from "framer-motion";
import { useTranslation } from "react-i18next";
import { sendChatMessage } from "../../services/api/chatApi";
import { speakText } from "../../utils/speech";

function NlpConsole() {
  const { t } = useTranslation();
  const [query, setQuery] = useState("");
  const [reply, setReply] = useState(t("nlp_default_reply"));
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [listening, setListening] = useState(false);
  const recognitionRef = useRef(null);

  useEffect(() => {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SR) return;
    const recognition = new SR();
    recognition.lang = "en-US";
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;
    recognitionRef.current = recognition;
  }, []);

  const runPrompt = async (textOverride) => {
    const text = (textOverride ?? query).trim();
    if (!text) return;
    setError("");
    setLoading(true);
    setReply(t("chat_thinking"));
    try {
      const answer = await sendChatMessage(text);
      setReply(answer);
      speakText(answer);
      setQuery("");
    } catch (e) {
      setError(e?.message || "Request failed");
      setReply(t("nlp_default_reply"));
    } finally {
      setLoading(false);
    }
  };

  const startMic = () => {
    const recognition = recognitionRef.current;
    if (!recognition) {
      setError(t("mic_not_supported"));
      return;
    }
    recognition.onstart = () => setListening(true);
    recognition.onend = () => setListening(false);
    recognition.onerror = () => setListening(false);
    recognition.onresult = (event) => {
      const said = event.results[0][0].transcript.trim();
      if (said) {
        setQuery(said);
        void runPrompt(said);
      }
    };
    try {
      recognition.start();
    } catch {
      setError(t("mic_busy"));
    }
  };

  return (
    <div className="glass-panel rounded-2xl p-5">
      <p className="text-xs tracking-[0.2em] text-leafPrimary">{t("nlp_title")}</p>
      <p className="mt-1 text-xs text-slate-400">{t("nlp_gemini_hint")}</p>
      <div className="mt-4 flex flex-col gap-3 sm:flex-row sm:items-stretch">
        <input
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          onKeyDown={(e) => e.key === "Enter" && !loading && void runPrompt()}
          placeholder={t("nlp_placeholder")}
          disabled={loading}
          className="input-shell flex-1 pt-4"
        />
        <div className="flex gap-2">
          <button
            type="button"
            title={t("mic_speak")}
            onClick={startMic}
            disabled={loading || listening}
            className="rounded-xl border border-white/20 bg-white/[0.06] px-4 py-3 text-lg leading-none text-slate-200 hover:bg-white/10 disabled:opacity-50"
          >
            {"\u{1F3A4}"}
          </button>
          <button
            type="button"
            onClick={() => void runPrompt()}
            disabled={loading || !query.trim()}
            className="rounded-xl border border-leafPrimary/50 bg-leafPrimary/10 px-5 py-3 text-sm font-semibold text-leafPrimary disabled:opacity-50"
          >
            {loading ? t("chat_thinking") : t("nlp_analyze")}
          </button>
        </div>
      </div>
      {listening && <p className="mt-2 text-xs text-leafSecondary">{t("mic_listening")}</p>}
      {error && <p className="mt-2 text-xs text-rose-400">{error}</p>}
      <motion.p
        key={reply}
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        className="mt-4 whitespace-pre-wrap text-sm text-slate-200"
      >
        {reply}
      </motion.p>
    </div>
  );
}

export default NlpConsole;
