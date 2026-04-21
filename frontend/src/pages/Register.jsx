import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { formatApiError } from "../api";

export default function Register() {
  const { register } = useAuth();
  const nav = useNavigate();
  const [form, setForm] = useState({ name: "", email: "", password: "" });
  const [err, setErr] = useState(""); const [loading, setLoading] = useState(false);
  const up = (k) => (e) => setForm(f => ({ ...f, [k]: e.target.value }));

  const submit = async (e) => {
    e.preventDefault(); setErr(""); setLoading(true);
    try { await register(form.email, form.password, form.name); nav("/onboarding"); }
    catch (e) { setErr(formatApiError(e)); } finally { setLoading(false); }
  };

  return (
    <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center px-6 starfield">
      <form onSubmit={submit} className="w-full max-w-md p-10 bg-[#1A0810]/90 border border-[#D4AF37]/20 backdrop-blur-md" data-testid="register-form">
        <p className="text-xs tracking-[0.3em] uppercase text-[#D4AF37] mb-3">Begin</p>
        <h1 className="font-serif text-4xl text-[#F3E6C6] mb-8">Cast your first chart</h1>
        {[
          { l: "Your name", k: "name", t: "text" },
          { l: "Email", k: "email", t: "email" },
          { l: "Password", k: "password", t: "password" },
        ].map(({ l, k, t }) => (
          <div key={k} className="mb-5">
            <label className="block text-xs tracking-[0.2em] uppercase text-[#8A6B72] mb-2">{l}</label>
            <input type={t} required value={form[k]} onChange={up(k)} data-testid={`register-${k}`}
              className="w-full bg-[#2A0E18] border border-[#D4AF37]/20 px-4 py-3 text-[#F3E6C6] outline-none focus:border-[#D4AF37]" />
          </div>
        ))}
        {err && <p className="text-sm text-[#E87B7B] mb-4" data-testid="register-error">{err}</p>}
        <button disabled={loading} type="submit" data-testid="register-submit"
          className="w-full py-3 bg-[#D4AF37] text-[#0A0305] font-medium uppercase tracking-[0.2em] text-sm hover:bg-[#B88A2A] transition disabled:opacity-60">
          {loading ? "Creating..." : "Create account"}
        </button>
        <p className="text-sm text-[#C2A3A8] mt-6 text-center">
          Already a seeker? <Link to="/login" className="text-[#D4AF37] hover:underline">Log in</Link>
        </p>
      </form>
    </div>
  );
}
