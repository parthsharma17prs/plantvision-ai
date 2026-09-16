import { fetchJson } from "./apiClient";

export async function sendChatMessage(message) {
  const data = await fetchJson("/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
  });
  return data.reply || "";
}
