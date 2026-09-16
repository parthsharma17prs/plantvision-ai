import { fetchJson } from "./apiClient";

export async function fetchLiveWeather(city) {
  const params = new URLSearchParams({ city: city.trim() });
  return fetchJson(`/weather?${params.toString()}`);
}

export async function fetchWeatherByCoords(lat, lon) {
  const params = new URLSearchParams({ lat: String(lat), lon: String(lon) });
  return fetchJson(`/weather?${params.toString()}`);
}
