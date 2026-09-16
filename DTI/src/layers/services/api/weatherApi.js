import { fetchJson } from "./apiClient";

export async function fetchLiveWeather(city) {
  const params = new URLSearchParams({ city: city.trim() });
  return fetchJson(`/weather?${params.toString()}`);
}
