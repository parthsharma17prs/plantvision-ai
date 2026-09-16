import { useState } from "react";
import { motion } from "framer-motion";
import Button from "../components/Button";

const defaultForm = { email: "", password: "", name: "" };

function FloatingInput({ name, type = "text", label, value, onChange }) {
  return (
    <label className="group relative block">
      <input
        name={name}
        type={type}
        value={value}
        onChange={onChange}
        placeholder=" "
        className="input-shell peer"
      />
      <span className="pointer-events-none absolute left-4 top-4 text-sm text-slate-400 transition-all peer-placeholder-shown:top-5 peer-placeholder-shown:text-base peer-focus:top-2 peer-focus:text-xs peer-focus:text-leafSecondary">
        {label}
      </span>
    </label>
  );
}

function Login() {
  const [mode, setMode] = useState("login");
  const [form, setForm] = useState(defaultForm);
  const [error, setError] = useState("");

  const handleChange = (event) => {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    if (!form.email || !form.password || (mode === "signup" && !form.name)) {
      setError("Please fill all required fields.");
      return;
    }

    setError("");
    localStorage.setItem("leafx-auth", JSON.stringify({ mode, email: form.email }));
  };

  return (
    <section className="page-shell flex min-h-[84vh] items-center">
      <motion.div
        initial={{ opacity: 0, y: 18 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.35 }}
        className="glass-panel mx-auto w-full max-w-md rounded-3xl border border-white/15 p-8"
      >
        <p className="text-xs tracking-[0.22em] text-leafPrimary">SECURE ACCESS</p>
        <h2 className="mt-3 text-3xl font-bold tracking-tight">{mode === "login" ? "Welcome back" : "Create account"}</h2>
        <p className="mt-2 text-sm text-slate-300">Access the LeafX disease intelligence suite.</p>

        <form onSubmit={handleSubmit} className="mt-6 space-y-4">
          {mode === "signup" && (
            <FloatingInput name="name" value={form.name} onChange={handleChange} label="Full Name" />
          )}
          <FloatingInput name="email" type="email" value={form.email} onChange={handleChange} label="Email" />
          <FloatingInput name="password" type="password" value={form.password} onChange={handleChange} label="Password" />

          {error && <p className="text-sm text-rose-400">{error}</p>}

          <Button type="submit" className="w-full">
            {mode === "login" ? "Login" : "Sign Up"}
          </Button>
        </form>

        <button
          type="button"
          onClick={() => {
            setMode((prev) => (prev === "login" ? "signup" : "login"));
            setError("");
          }}
          className="mt-5 text-sm font-medium tracking-wide text-leafPrimary transition hover:text-leafSecondary"
        >
          {mode === "login" ? "Need an account? Sign up" : "Already have an account? Login"}
        </button>
      </motion.div>
    </section>
  );
}

export default Login;
