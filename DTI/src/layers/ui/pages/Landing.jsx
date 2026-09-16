import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import Button from "../components/Button";
import NlpConsole from "../../ai/components/NlpConsole";

function Landing() {
  const { t } = useTranslation();

  return (
    <section className="page-shell space-y-8">
      <div className="glass-panel relative overflow-hidden rounded-3xl p-8 sm:p-12">
        <div className="pointer-events-none absolute inset-0 bg-[linear-gradient(120deg,rgba(0,255,156,0.08),rgba(0,207,255,0.08),rgba(0,255,156,0.08))]" />
        <div className="relative z-10 text-center">
          <p className="text-xs tracking-[0.24em] text-leafPrimary">{t("landing_badge")}</p>
          <h1 className="mt-4 text-4xl font-extrabold tracking-tight sm:text-5xl lg:text-6xl">{t("landing_title")}</h1>
          <p className="mx-auto mt-4 max-w-2xl text-sm text-slate-300 sm:text-base">{t("landing_subtitle")}</p>
          <div className="mt-8 flex flex-wrap justify-center gap-3">
            <Link to="/scan"><Button>{t("start_scan")}</Button></Link>
            <Link to="/weather"><Button variant="secondary">{t("check_weather")}</Button></Link>
            <Link to="/login"><Button>{t("login")}</Button></Link>
          </div>
        </div>
      </div>

      <NlpConsole />
    </section>
  );
}

export default Landing;
