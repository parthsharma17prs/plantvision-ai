import { fetchJson } from "./apiClient";

/**
 * Ask the backend (Gemini) for structured treatment advice for a predicted disease.
 */
export async function fetchDiseaseRecommendation({
  disease,
  severity = 0,
  plantHealth = 0,
  confidence = 0,
  staticHint = "",
}) {
  const data = await fetchJson("/api/recommendation", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      disease,
      severity,
      plantHealth,
      confidence,
      staticHint: staticHint,
    }),
  });
  return data.recommendation || "";
}
