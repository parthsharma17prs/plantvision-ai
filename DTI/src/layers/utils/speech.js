/** Strip simple markdown / noise for speech synthesis */
export function textForSpeech(text) {
  return String(text)
    .replace(/\*\*|__/g, "")
    .replace(/[#*`]/g, "")
    .trim();
}

export function speakText(text) {
  if (typeof window === "undefined" || !window.speechSynthesis) return;
  window.speechSynthesis.cancel();
  const u = new SpeechSynthesisUtterance(textForSpeech(text));
  u.lang = "en-US";
  window.speechSynthesis.speak(u);
}
