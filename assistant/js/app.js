/**
 * Plant Disease Assistant — frontend
 * Expects Flask on same origin (e.g. http://127.0.0.1:5173)
 */

const chatMessages = document.getElementById("chatMessages");
const chatInput = document.getElementById("chatInput");
const sendBtn = document.getElementById("sendBtn");
const micBtn = document.getElementById("micBtn");
const micStatus = document.getElementById("micStatus");

const cityInput = document.getElementById("cityInput");
const weatherBtn = document.getElementById("weatherBtn");
const weatherBody = document.getElementById("weatherBody");

const fileInput = document.getElementById("fileInput");
const predictBtn = document.getElementById("predictBtn");
const previewWrap = document.getElementById("previewWrap");
const previewImg = document.getElementById("previewImg");
const predictOut = document.getElementById("predictOut");

let selectedDataUrl = null;

function addMessage(text, role) {
  const div = document.createElement("div");
  div.className = `msg ${role}`;
  div.textContent = text;
  chatMessages.appendChild(div);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function stripForSpeech(text) {
  return text.replace(/\*\*|__/g, "").replace(/[#*`]/g, "").trim();
}

function speak(text) {
  if (!window.speechSynthesis) return;
  window.speechSynthesis.cancel();
  const u = new SpeechSynthesisUtterance(stripForSpeech(text));
  u.lang = "en-US";
  window.speechSynthesis.speak(u);
}

async function sendChat() {
  const message = chatInput.value.trim();
  if (!message) return;

  addMessage(message, "user");
  chatInput.value = "";
  sendBtn.disabled = true;

  try {
    const res = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });
    const data = await res.json();
    if (!res.ok) {
      addMessage(data.error || "Chat failed", "err");
      return;
    }
    const reply = data.reply || "";
    addMessage(reply, "bot");
    speak(reply);
  } catch (e) {
    addMessage(String(e), "err");
  } finally {
    sendBtn.disabled = false;
  }
}

sendBtn.addEventListener("click", sendChat);
chatInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") sendChat();
});

/* --- Web Speech API (speech-to-text) --- */
let recognition = null;
if ("webkitSpeechRecognition" in window || "SpeechRecognition" in window) {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  recognition = new SR();
  recognition.lang = "en-US";
  recognition.interimResults = false;
  recognition.maxAlternatives = 1;

  recognition.onstart = () => {
    micBtn.classList.add("listening");
    micStatus.textContent = "Listening… speak now.";
  };

  recognition.onend = () => {
    micBtn.classList.remove("listening");
    micStatus.textContent = "";
  };

  recognition.onerror = (ev) => {
    micStatus.textContent = "Mic error: " + (ev.error || "unknown");
    micBtn.classList.remove("listening");
  };

  recognition.onresult = (ev) => {
    const text = ev.results[0][0].transcript.trim();
    if (text) {
      chatInput.value = text;
      sendChat();
    }
  };
} else {
  micBtn.disabled = true;
  micStatus.textContent = "Speech recognition not supported in this browser.";
}

micBtn.addEventListener("click", () => {
  if (!recognition) return;
  try {
    recognition.start();
  } catch {
    micStatus.textContent = "Already listening…";
  }
});

/* --- Weather --- */
async function loadWeather() {
  const city = cityInput.value.trim();
  if (!city) {
    weatherBody.textContent = "Please enter a city name.";
    return;
  }
  weatherBody.textContent = "Loading…";
  weatherBody.classList.remove("muted");
  try {
    const params = new URLSearchParams({ city });
    const res = await fetch("/weather?" + params.toString());
    const data = await res.json();
    if (!res.ok) {
      weatherBody.textContent = data.error || "Weather request failed";
      weatherBody.classList.add("muted");
      return;
    }
    weatherBody.classList.remove("muted");
    weatherBody.innerHTML = `
      <div><strong>${escapeHtml(data.city)}</strong> — ${escapeHtml(data.description)}</div>
      <div>Temperature: <strong>${data.temp_c}°C</strong></div>
      <div>Humidity: <strong>${data.humidity}%</strong></div>
      <div>Rain (last 1h / estimate): <strong>${data.rain_mm} mm</strong></div>
      <div class="muted" style="margin-top:0.5rem">${escapeHtml(data.farming_tip)}</div>
    `;
  } catch (e) {
    weatherBody.textContent = String(e);
    weatherBody.classList.add("muted");
  }
}

function escapeHtml(s) {
  const d = document.createElement("div");
  d.textContent = s;
  return d.innerHTML;
}

weatherBtn.addEventListener("click", loadWeather);
cityInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") loadWeather();
});

/* --- Image → /predict --- */
fileInput.addEventListener("change", () => {
  const file = fileInput.files && fileInput.files[0];
  predictBtn.disabled = !file;
  selectedDataUrl = null;
  if (!file) {
    previewWrap.classList.add("hidden");
    return;
  }
  const reader = new FileReader();
  reader.onload = () => {
    selectedDataUrl = reader.result;
    previewImg.src = selectedDataUrl;
    previewWrap.classList.remove("hidden");
  };
  reader.readAsDataURL(file);
});

predictBtn.addEventListener("click", async () => {
  if (!selectedDataUrl) return;
  predictOut.textContent = "Analyzing…";
  predictBtn.disabled = true;
  try {
    const res = await fetch("/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ imageDataUrl: selectedDataUrl, conf: 0.2 }),
    });
    const data = await res.json();
    predictOut.textContent = JSON.stringify(data, null, 2);
    if (data.disease || data.reply) {
      const summary =
        data.disease && data.suggestion
          ? `Detected: ${data.disease}. ${data.suggestion}`
          : JSON.stringify(data);
      speak(summary);
    }
  } catch (e) {
    predictOut.textContent = String(e);
  } finally {
    predictBtn.disabled = false;
  }
});

/* Welcome */
addMessage(
  "Hi! Ask about plant diseases, crops, or soil. I only answer farming-related topics.",
  "bot"
);
