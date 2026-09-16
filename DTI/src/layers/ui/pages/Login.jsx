import { useState, useEffect } from "react";
import { useTranslation } from "react-i18next";
import { useNavigate } from "react-router-dom";
import Button from "../components/Button";
import { loginUser, signupUser } from "../../services/api/authApi";

function Login() {
  const { t } = useTranslation();
  const navigate = useNavigate();

  const [mode, setMode] = useState("login");
  const [form, setForm] = useState({ name: "", email: "", password: "" });
  const [showPassword, setShowPassword] = useState(false);
  const [successMessage, setSuccessMessage] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [sessionUser, setSessionUser] = useState(null);

  useEffect(() => {
    try {
      const raw = localStorage.getItem("plantvision-user");
      if (!raw) {
        setSessionUser(null);
        return;
      }
      const u = JSON.parse(raw);
      setSessionUser(u && typeof u === "object" && u.email ? u : null);
    } catch {
      setSessionUser(null);
    }
  }, []);

  const logout = () => {
    localStorage.removeItem("plantvision-user");
    setSessionUser(null);
    setSuccessMessage("");
    setErrorMessage("");
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setSuccessMessage("");
    setErrorMessage("");
    setSubmitting(true);
    try {
      if (mode === "signup") {
        const response = await signupUser(form);
        setSuccessMessage(response.message || "Signup successful");
        setMode("login");
      } else {
        const response = await loginUser({ email: form.email, password: form.password });
        setSuccessMessage(response.message || "Login successful");
        if (response.user) {
          localStorage.setItem("plantvision-user", JSON.stringify(response.user));
          navigate("/community");
        }
      }
      setForm((prev) => ({ ...prev, password: "" }));
    } catch (error) {
      setErrorMessage(error?.message || "Authentication failed");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <section className="page-shell flex min-h-[78vh] items-center">
      <div className="glass-panel mx-auto w-full max-w-md rounded-3xl p-8 relative overflow-hidden shadow-2xl">
        {/* Decorative Glows */}
        <div className="absolute -top-20 -right-20 w-40 h-40 bg-leafSecondary/10 blur-3xl rounded-full pointer-events-none"></div>
        <div className="absolute -bottom-20 -left-20 w-40 h-40 bg-leafPrimary/10 blur-3xl rounded-full pointer-events-none"></div>
        
        <div className="relative z-10">
          {sessionUser && (
            <div className="mb-6 rounded-2xl border border-leafSecondary/30 bg-leafSecondary/5 p-4 text-sm">
              <p className="text-slate-200">
                {t("login_already_signed_in", "Signed in as")}{" "}
                <span className="font-semibold text-leafSecondary">{sessionUser.email}</span>
              </p>
              <div className="mt-3 flex flex-wrap gap-2">
                <Button type="button" variant="secondary" className="!px-4 !py-2 text-xs" onClick={() => navigate("/community")}>
                  {t("login_go_community", "Go to Community")}
                </Button>
                <button
                  type="button"
                  onClick={logout}
                  className="rounded-full border border-white/20 px-4 py-2 text-xs text-slate-300 hover:bg-white/10"
                >
                  {t("login_sign_out", "Sign out")}
                </button>
              </div>
            </div>
          )}
          {/* Tab Headers */}
          <div className="flex space-x-6 border-b border-white/10 mb-8 pb-1">
            <button
              type="button"
              onClick={() => { setMode("login"); setErrorMessage(""); setSuccessMessage(""); }}
              className={`pb-2 text-lg font-bold transition-all relative ${mode === "login" ? "text-leafSecondary" : "text-slate-400 hover:text-slate-200"}`}
            >
              {t("login", "Login")}
              {mode === "login" && <span className="absolute bottom-0 left-0 w-full h-0.5 bg-leafSecondary rounded-t-full" style={{ boxShadow: "0 0 8px #00ff9c" }}></span>}
            </button>
            <button
              type="button"
              onClick={() => { setMode("signup"); setErrorMessage(""); setSuccessMessage(""); }}
              className={`pb-2 text-lg font-bold transition-all relative ${mode === "signup" ? "text-leafPrimary" : "text-slate-400 hover:text-slate-200"}`}
            >
              {t("signup", "Register")}
              {mode === "signup" && <span className="absolute bottom-0 left-0 w-full h-0.5 bg-leafPrimary rounded-t-full" style={{ boxShadow: "0 0 8px #00cfff" }}></span>}
            </button>
          </div>

          <div>
            <h2 className="text-2xl font-bold">{mode === "login" ? t("login_welcome", "Welcome Back") : t("signup_welcome", "Join the Community")}</h2>
            <p className="mt-2 text-sm text-slate-300">{mode === "login" ? t("login_subtitle", "Log in to access your farm dashboard.") : t("signup_subtitle", "Create an account to start sharing.")}</p>
          </div>

          <form onSubmit={handleSubmit} className="mt-8 space-y-5">
            {mode === "signup" && (
              <input
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                placeholder={t("full_name")}
                className="input-shell pt-4"
              />
            )}
            <input
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
              placeholder={t("email")}
              className="input-shell pt-4"
            />
            
            <div className="relative">
              <input
                type={showPassword ? "text" : "password"}
                value={form.password}
                onChange={(e) => setForm({ ...form, password: e.target.value })}
                placeholder={t("password")}
                className="input-shell pt-4 w-full"
              />
              <button
                type="button"
                onClick={() => setShowPassword((prev) => !prev)}
                className="absolute right-4 top-1/2 -translate-y-1/2 text-xs font-semibold text-slate-400 hover:text-white transition-colors"
              >
                {showPassword ? "HIDE" : "SHOW"}
              </button>
            </div>

            <div className="pt-2">
              <Button className="w-full" disabled={submitting} variant={mode === "login" ? "primary" : "secondary"}>
                {submitting ? "Processing..." : mode === "login" ? t("login") : t("create_account")}
              </Button>
            </div>

            {successMessage && <p className="text-sm text-emerald-400 text-center">{successMessage}</p>}
            {errorMessage && <p className="text-sm text-rose-400 text-center">{errorMessage}</p>}
          </form>
        </div>
      </div>
    </section>
  );
}

export default Login;
