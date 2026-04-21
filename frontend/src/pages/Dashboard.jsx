import { useEffect, useState } from "react";
import api from "../api";
import MatchCard from "../components/MatchCard";
import { Lock, Sparkle } from "@phosphor-icons/react";
import { toast } from "sonner";

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [loadingPay, setLoadingPay] = useState(false);

  useEffect(() => {
    api.get("/matches").then(r => setData(r.data)).catch(() => setData({ status: "waiting", low: [], high: [] }));
  }, []);

  const unlock = async () => {
    setLoadingPay(true);
    try {
      const { data: r } = await api.post("/payments/checkout", { origin_url: window.location.origin });
      window.location.href = r.url;
    } catch (e) {
      toast.error("Unable to start payment. Please try again.");
      setLoadingPay(false);
    }
  };

  if (!data) return <div className="p-16 text-center text-[#8A6B72]">Aligning...</div>;

  const { low = [], high = [], unlocked_count = 0, total_high = 0, remaining_locked = 0 } = data;

  return (
    <div className="min-h-[calc(100vh-4rem)] px-6 md:px-10 py-12 max-w-7xl mx-auto" data-testid="dashboard">
      <div className="mb-12">
        <p className="text-xs tracking-[0.3em] uppercase text-[#D4AF37] mb-3">Your constellation</p>
        <h1 className="font-serif text-4xl sm:text-5xl text-[#F3E6C6]">Dashboard</h1>
        <div className="flex flex-wrap gap-6 mt-6 text-sm text-[#C2A3A8]">
          <Stat label="Casual (0–17)" value={low.length} />
          <Stat label="Premium (18–36)" value={total_high} />
          <Stat label="Unlocked" value={unlocked_count} />
        </div>
      </div>

      {/* Low compat */}
      <section className="mb-16">
        <div className="flex items-center justify-between mb-6">
          <h2 className="font-serif text-3xl text-[#F3E6C6]">Your matches</h2>
          <span className="text-xs uppercase tracking-[0.2em] text-[#8A6B72]">Score &lt; 18 · always free</span>
        </div>
        {low.length === 0 ? (
          <p className="text-[#8A6B72] italic">No casual matches right now. The stars favour the rarer connection for you.</p>
        ) : (
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {low.map(m => <MatchCard key={m.match_user_id} match={m} />)}
          </div>
        )}
      </section>

      {/* High compat */}
      <section>
        <div className="flex items-center justify-between mb-6">
          <h2 className="font-serif text-3xl text-[#F3E6C6]">High compatibility</h2>
          <span className="text-xs uppercase tracking-[0.2em] text-[#D4AF37]">Score ≥ 18</span>
        </div>

        {high.length === 0 ? (
          <p className="text-[#8A6B72] italic">No premium matches yet — keep your profile fresh; new seekers arrive daily.</p>
        ) : (
          <>
            {remaining_locked > 0 && (
              <div className="mb-8 p-8 border border-[#D4AF37]/30 bg-gradient-to-r from-[#2A0E18] to-[#1A0810]" data-testid="paywall-banner">
                <div className="flex flex-col md:flex-row gap-6 items-start md:items-center justify-between">
                  <div className="flex items-start gap-4">
                    <div className="w-12 h-12 rounded-full bg-[#D4AF37]/10 border border-[#D4AF37]/30 flex items-center justify-center flex-shrink-0">
                      <Sparkle size={22} weight="fill" className="text-[#D4AF37]" />
                    </div>
                    <div>
                      <p className="text-xs tracking-[0.3em] uppercase text-[#D4AF37] mb-2">You have {total_high}+ high-compatibility connections</p>
                      <h3 className="font-serif text-2xl text-[#F3E6C6] mb-1">Unlock 5 connections for ₹1,000</h3>
                      <p className="text-sm text-[#C2A3A8]">{remaining_locked} still locked. Payment reveals contact, kundali report & PDF.</p>
                    </div>
                  </div>
                  <button onClick={unlock} disabled={loadingPay} data-testid="unlock-premium-button"
                    className="px-8 py-3.5 bg-[#D4AF37] text-[#0A0305] font-medium uppercase tracking-[0.2em] text-xs hover:bg-[#B88A2A] transition disabled:opacity-60 whitespace-nowrap">
                    {loadingPay ? "Redirecting..." : "Unlock now ₹1,000"}
                  </button>
                </div>
              </div>
            )}
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {high.map((m, i) => (
                <div key={i} className="relative">
                  <MatchCard match={m} locked={m.locked} />
                  {m.locked && (
                    <div className="absolute inset-0 premium-card-lock border border-[#D4AF37]/30 flex flex-col items-center justify-center text-center p-6">
                      <Lock size={28} weight="duotone" className="text-[#D4AF37] mb-3" />
                      <p className="text-xs tracking-[0.3em] uppercase text-[#D4AF37] mb-2">Locked</p>
                      <p className="font-serif text-3xl text-[#F3E6C6] mb-1">{m.score}/36</p>
                      <p className="text-sm text-[#C2A3A8] mb-4">High compatibility</p>
                      <button onClick={unlock} disabled={loadingPay} data-testid={`unlock-card-${i}`}
                        className="px-5 py-2 bg-[#D4AF37] text-[#0A0305] uppercase tracking-[0.2em] text-[10px] hover:bg-[#B88A2A]">
                        Unlock · ₹1,000
                      </button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </>
        )}
      </section>
    </div>
  );
}

function Stat({ label, value }) {
  return (
    <div className="px-5 py-3 bg-[#1A0810] border border-[#D4AF37]/15">
      <div className="text-[10px] tracking-[0.3em] uppercase text-[#8A6B72]">{label}</div>
      <div className="font-serif text-2xl text-[#F3E6C6]">{value}</div>
    </div>
  );
}
