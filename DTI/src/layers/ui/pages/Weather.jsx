import { useState } from "react";
import { useTranslation } from "react-i18next";
import Card from "../components/Card";
import Button from "../components/Button";
import { fetchLiveWeather, fetchWeatherByCoords } from "../../services/api/weatherApi";

function Weather() {
  const { t } = useTranslation();
  const [city, setCity] = useState("");
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [locating, setLocating] = useState(false);

  const loadWeather = async () => {
    if (!city.trim()) {
      setError(t("weather_city_required", "Please enter a city name."));
      return;
    }
    setError("");
    setLoading(true);
    try {
      const w = await fetchLiveWeather(city);
      setData(w);
    } catch (e) {
      setData(null);
      setError(e?.message || t("weather_error"));
    } finally {
      setLoading(false);
    }
  };

  const getLiveLocation = () => {
    if (!navigator.geolocation) {
      setError(t("weather_geo_unsupported", "Geolocation is not supported by your browser."));
      return;
    }

    setError("");
    setLocating(true);

    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        try {
          const lat = pos.coords.latitude;
          const lon = pos.coords.longitude;
          const w = await fetchWeatherByCoords(lat, lon);
          setData(w);
          if (w.city) {
            setCity(w.city);
          }
        } catch (e) {
          setError(e?.message || t("weather_error"));
        } finally {
          setLocating(false);
        }
      },
      (geoErr) => {
        setLocating(false);
        switch (geoErr.code) {
          case geoErr.PERMISSION_DENIED:
            setError(t("weather_geo_denied", "Location permission denied. Please allow location access or enter your city manually."));
            break;
          case geoErr.POSITION_UNAVAILABLE:
            setError(t("weather_geo_unavailable", "Location information is unavailable. Please enter your city manually."));
            break;
          case geoErr.TIMEOUT:
            setError(t("weather_geo_timeout", "Location request timed out. Please try again or enter your city."));
            break;
          default:
            setError(geoErr.message || t("weather_geo_unavailable", "Unable to retrieve your location."));
        }
      },
      { timeout: 12000, enableHighAccuracy: true, maximumAge: 60000 }
    );
  };

  const tempLabel = data ? `${data.temp_c}°C` : "—";
  const humidityLabel = data ? `${data.humidity}%` : "—";
  const conditionLabel = data?.description || "—";
  const rainLabel = data ? `${data.rain_mm} mm` : "—";

  return (
    <section className="page-shell space-y-6">
      <h2 className="text-3xl font-bold">{t("weather_title")}</h2>

      <div className="glass-panel flex flex-col gap-3 rounded-2xl p-4 sm:flex-row sm:items-end">
        <div className="flex-1">
          <label className="text-xs text-slate-400">{t("weather_city_label")}</label>
          <input
            value={city}
            onChange={(e) => setCity(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && void loadWeather()}
            placeholder={t("weather_city_placeholder")}
            className="input-shell mt-1 w-full pt-3"
          />
        </div>
        <div className="flex flex-wrap gap-2">
          <Button onClick={() => void loadWeather()} disabled={loading || locating}>
            {loading ? t("weather_loading") : t("weather_fetch")}
          </Button>
          <Button
            variant="secondary"
            onClick={getLiveLocation}
            disabled={loading || locating}
            className="flex items-center gap-2"
          >
            {locating ? (
              <>
                <svg className="h-4 w-4 animate-spin text-leafSecondary" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
                </svg>
                {t("weather_locating", "Detecting…")}
              </>
            ) : (
              <>
                <span>📍</span>
                {t("weather_live_location", "Get Live Location")}
              </>
            )}
          </Button>
        </div>
      </div>

      {error && <p className="text-sm text-rose-400">{error}</p>}

      {data && (
        <div className="flex flex-wrap items-center justify-between gap-2 text-sm text-slate-300">
          <p>
            {t("weather_showing_for")}: <strong className="text-leafSecondary">{data.city}</strong>
            {data.coord?.lat && data.coord?.lon && (
              <span className="ml-2 font-mono text-xs text-slate-400">
                ({data.coord.lat.toFixed(4)}°N, {data.coord.lon.toFixed(4)}°E)
              </span>
            )}
          </p>
          <span className="rounded-full border border-emerald-500/20 bg-emerald-500/10 px-3 py-1 text-xs text-emerald-400">
            ● Live GPS Sync
          </span>
        </div>
      )}

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card title={t("temperature")} value={tempLabel} subtitle={t("field_temperature")} />
        <Card title={t("humidity")} value={humidityLabel} subtitle={t("moisture_profile")} />
        <Card title={t("condition")} value={conditionLabel} subtitle={t("sky_condition")} />
        <Card title={t("rain_last_hour")} value={rainLabel} subtitle={t("openweather_rain_hint")} />
      </div>

      <div className="glass-panel rounded-2xl p-5">
        <p className="text-xs tracking-[0.2em] text-leafPrimary">{t("farming_tip_title")}</p>
        <p className="mt-3 text-sm text-slate-200">
          {data?.farming_tip || t("weather_tip_placeholder")}
        </p>
      </div>
    </section>
  );
}

export default Weather;
