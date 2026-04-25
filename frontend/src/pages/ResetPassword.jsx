import { useState } from "react";
import { Link, useParams, useNavigate } from "react-router-dom";
import api, { formatApiError } from "../api";
import { useAuth } from "../context/AuthContext";

export default function ResetPassword() {
  const { token } = useParams();
  const nav = useNavigate();
  const { setUser } = useAuth();
  const [pwd, setPwd] = useState("");
  const [pwd2, setPwd2] = useState("");
  const [err, setErr] = useState("");
  const [busy, setBusy] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setErr("");
    if (pwd.length < 6) { setErr("Password must be at least 6 characters."); return; }
    if (pwd !== pwd2) { setErr("Passwords don't match."); return; }
    setBusy(true);
    try {
      const { data } = await api.post("/auth/reset-password", { token, new_password: pwd });
      setUser(data);
      nav(data.profile_complete ? "/dashboard" : "/onboarding");
    } catch (e) { setErr(formatApiError(e)); }
    finally { setBusy(false); }
  };

  return (
    <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center px-6 starfield">
      <form onSubmit={submit} className="w-full max-w-md p-10 bg-[#1A0810]/90 border border-[#D4AF37]/20 backdrop-blur-md" data-testid="reset-form">
        <p className="text-xs tracking-[0.3em] uppercase text-[#D4AF37] mb-3">New password</p>
        <h1 className="font-serif text-4xl text-[#F3E6C6] mb-8">Set a new password</h1>

        <label className="block text-xs tracking-[0.2em] uppercase text-[#8A6B72] mb-2">New password</label>
        <input type="password" required value={pwd} onChange={e => setPwd(e.target.value)} data-testid="reset-password"
          className="w-full bg-[#2A0E18] border border-[#D4AF37]/20 px-4 py-3 text-[#F3E6C6] outline-none focus:border-[#D4AF37] mb-5" />

        <label className="block text-xs tracking-[0.2em] uppercase text-[#8A6B72] mb-2">Confirm password</label>
        <input type="password" required value={pwd2} onChange={e => setPwd2(e.target.value)} data-testid="reset-password-confirm"
          className="w-full bg-[#2A0E18] border border-[#D4AF37]/20 px-4 py-3 text-[#F3E6C6] outline-none focus:border-[#D4AF37] mb-6" />

        {err && <p className="text-sm text-[#E87B7B] mb-4" data-testid="reset-error">{err}</p>}
        <button disabled={busy} type="submit" data-testid="reset-submit"
          className="w-full py-3 bg-[#D4AF37] text-[#0A0305] font-medium uppercase tracking-[0.2em] text-sm hover:bg-[#B88A2A] disabled:opacity-60">
          {busy ? "Setting…" : "Set new password"}
        </button>

        <p className="text-sm text-[#C2A3A8] mt-6 text-center">
          <Link to="/login" className="text-[#D4AF37] hover:underline">Back to login</Link>
        </p>
      </form>
    </div>
  );
}
