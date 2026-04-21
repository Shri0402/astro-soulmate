import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import api from "../api";
import { useAuth } from "../context/AuthContext";
import { CheckCircle, XCircle } from "@phosphor-icons/react";

export default function PaymentSuccess() {
  const [params] = useSearchParams();
  const sessionId = params.get("session_id");
  const { refreshUser } = useAuth();
  const [state, setState] = useState({ status: "polling", message: "Verifying your payment..." });

  useEffect(() => {
    if (!sessionId) { setState({ status: "error", message: "Missing session." }); return; }
    let attempts = 0; let stopped = false;
    const poll = async () => {
      if (stopped) return;
      if (attempts >= 12) { setState({ status: "error", message: "Timed out — please refresh or contact support." }); return; }
      try {
        const { data } = await api.get(`/payments/status/${sessionId}`);
        if (data.payment_status === "paid") {
          await refreshUser();
          setState({ status: "ok", message: `5 premium matches unlocked. Total unlocked: ${data.unlocked_premium}.` });
          return;
        }
        if (data.status === "expired") { setState({ status: "error", message: "Session expired." }); return; }
      } catch {}
      attempts += 1;
      setTimeout(poll, 2000);
    };
    poll();
    return () => { stopped = true; };
  }, [sessionId, refreshUser]);

  const ok = state.status === "ok";
  const err = state.status === "error";

  return (
    <div className="min-h-[calc(100vh-4rem)] starfield flex items-center justify-center px-6">
      <div className="max-w-md text-center p-10 bg-[#1A0810]/90 border border-[#D4AF37]/25" data-testid="payment-result">
        {ok && <CheckCircle size={64} weight="duotone" className="text-[#D4AF37] mx-auto mb-5" />}
        {err && <XCircle size={64} weight="duotone" className="text-[#E87B7B] mx-auto mb-5" />}
        {!ok && !err && <div className="w-12 h-12 mx-auto mb-5 border-2 border-[#D4AF37] border-t-transparent rounded-full animate-spin" />}
        <p className="text-xs tracking-[0.3em] uppercase text-[#D4AF37] mb-3">
          {ok ? "Stars aligned" : err ? "Something went amiss" : "Consulting Stripe"}
        </p>
        <h1 className="font-serif text-3xl text-[#F3E6C6] mb-4">
          {ok ? "Payment successful" : err ? "Payment unverified" : "Verifying…"}
        </h1>
        <p className="text-[#C2A3A8] mb-8">{state.message}</p>
        <Link to="/dashboard" className="inline-block px-8 py-3 bg-[#D4AF37] text-[#0A0305] uppercase tracking-[0.2em] text-xs hover:bg-[#B88A2A]" data-testid="back-to-dashboard">
          Return to dashboard
        </Link>
      </div>
    </div>
  );
}
