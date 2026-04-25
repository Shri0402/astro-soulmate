import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { formatApiError } from "../api";

export default function Login() {
  const { login } = useAuth();
  const nav = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [err, setErr] = useState("");
  const [loading, setLoading] = useState(false);

  const submit = async (e) => {
    e.preventDefault(); setErr(""); setLoading(true);
    try {
      const u = await login(email, password);
      nav(u.profile_complete ? "/dashboard" : "/onboarding");
    } catch (e) { setErr(formatApiError(e)); } finally { setLoading(false); }
  };

  return (
    <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center px-6 starfield">
      <form onSubmit={submit} className="w-full max-w-md p-10 bg-[#1A0810]/90 border border-[#D4AF37]/20 backdrop-blur-md" data-testid="login-form">
        <p className="text-xs tracking-[0.3em] uppercase text-[#D4AF37] mb-3">Welcome back</p>
        <h1 className="font-serif text-4xl text-[#F3E6C6] mb-8">Realign your stars</h1>
        <label className="block text-xs tracking-[0.2em] uppercase text-[#8A6B72] mb-2">Email</label>
        <input type="email" required value={email} onChange={e => setEmail(e.target.value)} data-testid="login-email"
          className="w-full bg-[#2A0E18] border border-[#D4AF37]/20 px-4 py-3 text-[#F3E6C6] outline-none focus:border-[#D4AF37] mb-5" />
        <label className="block text-xs tracking-[0.2em] uppercase text-[#8A6B72] mb-2">Password</label>
        <input type="password" required value={password} onChange={e => setPassword(e.target.value)} data-testid="login-password"
          className="w-full bg-[#2A0E18] border border-[#D4AF37]/20 px-4 py-3 text-[#F3E6C6] outline-none focus:border-[#D4AF37] mb-6" />
        {err && <p className="text-sm text-[#E87B7B] mb-4" data-testid="login-error">{err}</p>}
        <button disabled={loading} type="submit" data-testid="login-submit"
          className="w-full py-3 bg-[#D4AF37] text-[#0A0305] font-medium uppercase tracking-[0.2em] text-sm hover:bg-[#B88A2A] transition disabled:opacity-60">
          {loading ? "Entering..." : "Enter"}
        </button>
        <p className="text-sm text-[#C2A3A8] mt-4 text-center">
          <Link to="/forgot-password" className="text-[#8A6B72] hover:text-[#D4AF37]" data-testid="forgot-link">Forgot password?</Link>
        </p>
        <p className="text-sm text-[#C2A3A8] mt-2 text-center">
          New here? <Link to="/register" className="text-[#D4AF37] hover:underline">Cast your chart</Link>
        </p>
      </form>
    </div>
  );
}
