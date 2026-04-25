import { useState } from "react";
import { Link } from "react-router-dom";
import api, { formatApiError } from "../api";

export default function ForgotPassword() {
  const [email, setEmail] = useState("");
  const [state, setState] = useState({ status: "idle", message: "", devLink: "" });

  const submit = async (e) => {
    e.preventDefault();
    setState({ status: "loading", message: "" });
    try {
      const { data } = await api.post("/auth/forgot-password", { email });
      setState({ status: "ok", message: data.message, devLink: data.dev_link || "" });
    } catch (e) {
      setState({ status: "err", message: formatApiError(e) });
    }
  };

  return (
    <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center px-6 starfield">
      <form onSubmit={submit} className="w-full max-w-md p-10 bg-[#1A0810]/90 border border-[#D4AF37]/20 backdrop-blur-md" data-testid="forgot-form">
        <p className="text-xs tracking-[0.3em] uppercase text-[#D4AF37] mb-3">Recover access</p>
        <h1 className="font-serif text-4xl text-[#F3E6C6] mb-3">Reset password</h1>
        <p className="text-sm text-[#C2A3A8] mb-8">Enter your member email — we'll send a single-use reset link valid for 30 minutes.</p>

        <label className="block text-xs tracking-[0.2em] uppercase text-[#8A6B72] mb-2">Email</label>
        <input type="email" required value={email} onChange={e => setEmail(e.target.value)} data-testid="forgot-email"
          className="w-full bg-[#2A0E18] border border-[#D4AF37]/20 px-4 py-3 text-[#F3E6C6] outline-none focus:border-[#D4AF37] mb-6" />

        <button disabled={state.status === "loading"} type="submit" data-testid="forgot-submit"
          className="w-full py-3 bg-[#D4AF37] text-[#0A0305] font-medium uppercase tracking-[0.2em] text-sm hover:bg-[#B88A2A] disabled:opacity-60">
          {state.status === "loading" ? "Sending…" : "Send reset link"}
        </button>

        {state.status === "ok" && (
          <div className="mt-6 p-4 bg-[#0A0305]/50 border-l-2 border-[#D4AF37]" data-testid="forgot-result">
            <p className="text-sm text-[#F3E6C6]">{state.message}</p>
            {state.devLink && (
              <>
                <p className="text-xs uppercase tracking-[0.2em] text-[#D4AF37] mt-3">Dev link (email provider not configured)</p>
                <a href={state.devLink} className="text-xs text-[#D4AF37] underline break-all" data-testid="forgot-dev-link">{state.devLink}</a>
              </>
            )}
          </div>
        )}
        {state.status === "err" && <p className="mt-4 text-sm text-[#E87B7B]">{state.message}</p>}

        <p className="text-sm text-[#C2A3A8] mt-6 text-center">
          Remembered? <Link to="/login" className="text-[#D4AF37] hover:underline">Back to login</Link>
        </p>
      </form>
    </div>
  );
}
