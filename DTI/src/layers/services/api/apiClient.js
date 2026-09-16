const API_BASE = import.meta.env.VITE_API_BASE_URL || "";

function buildUrl(path) {
  const p = path.startsWith("/") ? path : `/${path}`;
  return `${API_BASE}${p}`;
}

/**
 * Fetch JSON from Flask. Detects HTML (SPA fallback) and throws a clear error.
 */
export async function fetchJson(path, init = {}) {
  const response = await fetch(buildUrl(path), init);
  const text = await response.text();
  const trimmed = text.trim();
  if (trimmed.startsWith("<!") || trimmed.toLowerCase().startsWith("<html")) {
    throw new Error(
      "Got a web page instead of JSON — the request did not reach the Flask API. " +
        "Run: cd DTI && npm run build, then start Flask (python app.py) and open http://127.0.0.1:5173. " +
        "If you use npm run dev, set VITE_API_BASE_URL in DTI/.env to your Flask URL."
    );
  }
  let data;
  try {
    data = JSON.parse(text);
  } catch {
    const preview = text.length > 280 ? `${text.slice(0, 280)}…` : text;
    const hint =
      !text.trim().length
        ? "Empty response — is Flask running? Start: start_backend.cmd or venv\\Scripts\\python.exe app.py"
        : preview.startsWith("Traceback")
          ? "Flask crashed (Python traceback). Check the terminal running app.py."
          : `Raw response was not JSON. ${preview ? `Preview: ${preview}` : ""}`;
    throw new Error(
      `Server did not return valid JSON. ${hint} If you use npm run dev, set VITE_API_BASE_URL=http://127.0.0.1:5000 in DTI/.env`
    );
  }
  if (!response.ok) {
    throw new Error(data?.error || `Request failed (${response.status})`);
  }
  return data;
}
