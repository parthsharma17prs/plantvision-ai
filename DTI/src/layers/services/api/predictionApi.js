import { fetchJson } from "./apiClient";

export async function runPrediction(imageDataUrl, conf = 0.2) {
  return fetchJson("/api/predict", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ imageDataUrl, conf }),
  });
}

export async function getPredictionHistory() {
  return fetchJson("/api/history");
}

export async function getDriveStatus() {
  return fetchJson("/api/drive/status");
}

export async function syncDriveNow() {
  return fetchJson("/api/drive/sync", { method: "POST" });
}

export async function getLatestResult() {
  return fetchJson("/api/latest-result");
}

export async function diagnosePest(imageDataUrl, disease = "Unknown") {
  return fetchJson("/api/diagnose/pest", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ imageDataUrl, disease }),
  });
}

export async function diagnoseNutrition(imageDataUrl, disease = "Unknown") {
  return fetchJson("/api/diagnose/nutrition", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ imageDataUrl, disease }),
  });
}
