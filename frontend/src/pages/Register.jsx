import { useState, useEffect } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import api, { formatApiError } from "../api";

export default function Register() {
  const { register } = useAuth();
  const nav = useNavigate();
  const { code: codeParam } = useParams();
  const [form, setForm] = useState({ name: "", email: "", password: "", invite_code: codeParam || "" });
  const [err, setErr] = useState("");
  const [loading, setLoading] = useState(false);
  const [inviteOk, setInviteOk] = useState(null);
  const [referrer, setReferrer] = useState("");

  const up = (k) => (e) => setForm(f => ({ ...f, [k]: e.target.value }));

  const validate = async (code) => {
    if (!code) { setInviteOk(null); setReferrer(""); return; }
    try {
      const { data } = await api.get(`/auth/invite/${code.toUpperCase()}`);
      setInviteOk(true); setReferrer(data.referrer_name || "");
    } catch { setInviteOk(false); setReferrer(""); }
  };

  useEffect(() => { if (codeParam) validate(codeParam); /* eslint-disable-next-line */ }, [codeParam]);

  const submit = async (e) => {
    e.preventDefault(); setErr(""); setLoading(true);
    try { await register(form.email, form.password, form.name, form.invite_code.toUpperCase()); nav("/onboarding"); }
    catch (e) { setErr(formatApiError(e)); } finally { setLoading(false); }
  };

  return (
    <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center px-6 starfield">
      <form onSubmit={submit} className="w-full max-w-md p-10 bg-[#1A0810]/90 border border-[#D4AF37]/20 backdrop-blur-md" data-testid="register-form">
        <p className="text-xs tracking-[0.3em] uppercase text-[#D4AF37] mb-3">Private Network</p>
        <h1 className="font-serif text-4xl text-[#F3E6C6] mb-3">By invitation only</h1>
        <p className="text-sm text-[#C2A3A8] mb-8">Stars Connection is a private referral-only matchmaking circle. Enter the invite code shared with you.</p>

        <Field l="Invite code">
          <input value={form.invite_code} onChange={(e) => { up("invite_code")(e); validate(e.target.value); }}
            data-testid="register-invite" required
            className={`w-full bg-[#2A0E18] border px-4 py-3 text-[#F3E6C6] outline-none uppercase tracking-widest font-mono ${
              inviteOk === false ? 'border-[#E87B7B]' : inviteOk === true ? 'border-[#D4AF37]' : 'border-[#D4AF37]/20 focus:border-[#D4AF37]'
            }`} />
          {inviteOk === true && referrer && <p className="text-xs text-[#D4AF37] mt-1">Referred by {referrer}</p>}
          {inviteOk === false && <p className="text-xs text-[#E87B7B] mt-1">Invalid or already-used code.</p>}
        </Field>

        {[{l:"Your name",k:"name",t:"text"},{l:"Email",k:"email",t:"email"},{l:"Password",k:"password",t:"password"}].map(({l,k,t}) => (
          <Field key={k} l={l}>
            <input type={t} required value={form[k]} onChange={up(k)} data-testid={`register-${k}`}
              className="w-full bg-[#2A0E18] border border-[#D4AF37]/20 px-4 py-3 text-[#F3E6C6] outline-none focus:border-[#D4AF37]" />
          </Field>
        ))}
        {err && <p className="text-sm text-[#E87B7B] mb-4" data-testid="register-error">{err}</p>}
        <button disabled={loading || inviteOk !== true} type="submit" data-testid="register-submit"
          className="w-full py-3 bg-[#D4AF37] text-[#0A0305] font-medium uppercase tracking-[0.2em] text-sm hover:bg-[#B88A2A] transition disabled:opacity-40">
          {loading ? "Joining..." : "Accept invitation"}
        </button>
        <p className="text-sm text-[#C2A3A8] mt-6 text-center">
          Already a member? <Link to="/login" className="text-[#D4AF37] hover:underline">Log in</Link>
        </p>
      </form>
    </div>
  );
}

function Field({ l, children }) {
  return (
    <div className="mb-5">
      <label className="block text-xs tracking-[0.2em] uppercase text-[#8A6B72] mb-2">{l}</label>
      {children}
    </div>
  );
}
