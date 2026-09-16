import { useState } from "react";
import { useTranslation } from "react-i18next";
import Card from "../components/Card";
import Button from "../components/Button";
import { fetchLiveWeather } from "../../services/api/weatherApi";

function Weather() {
  const { t } = useTranslation();
  const [city, setCity] = useState("");
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const loadWeather = async () => {
    if (!city.trim()) {
      setError(t("weather_city_required"));
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
        <Button onClick={() => void loadWeather()} disabled={loading}>
          {loading ? t("weather_loading") : t("weather_fetch")}
        </Button>
      </div>
      {error && <p className="text-sm text-rose-400">{error}</p>}
      {data && (
        <p className="text-sm text-slate-300">
          {t("weather_showing_for")}: <strong>{data.city}</strong>
        </p>
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
