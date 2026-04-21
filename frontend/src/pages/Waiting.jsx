import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api";

export default function Waiting() {
  const nav = useNavigate();
  const [checking, setChecking] = useState(false);

  useEffect(() => {
    const tick = async () => {
      setChecking(true);
      try {
        const { data } = await api.get("/matches");
        if (data.status === "ready") nav("/dashboard");
        else if (data.status === "needs_profile") nav("/onboarding");
      } finally { setChecking(false); }
    };
    tick();
    const iv = setInterval(tick, 6000);
    return () => clearInterval(iv);
  }, [nav]);

  return (
    <div className="min-h-[calc(100vh-4rem)] starfield flex items-center justify-center px-6">
      <div className="text-center max-w-xl" data-testid="waiting-room">
        <div className="relative w-48 h-48 mx-auto mb-10">
          <div className="absolute inset-0 rounded-full border border-[#D4AF37]/40 animate-slow-spin" />
          <div className="absolute inset-6 rounded-full border border-[#D4AF37]/25 animate-reverse-spin" />
          <div className="absolute inset-12 rounded-full border border-[#D4AF37]/15 animate-slow-spin" />
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-3 h-3 rounded-full bg-[#D4AF37] twinkle" />
          </div>
        </div>
        <p className="text-xs tracking-[0.3em] uppercase text-[#D4AF37] mb-4">Consulting the stars</p>
        <h1 className="font-serif text-4xl text-[#F3E6C6] mb-4">Your matches are being woven</h1>
        <p className="text-[#C2A3A8] leading-relaxed">
          No compatible charts are ready yet. As fellow seekers complete their kundali, we automatically surface them for you. This page will redirect the moment your first match appears.
        </p>
        <p className="text-xs uppercase tracking-[0.2em] text-[#8A6B72] mt-10">
          {checking ? "Re-checking..." : "Auto-refreshes every 6s"}
        </p>
      </div>
    </div>
  );
}
