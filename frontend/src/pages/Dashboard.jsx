import { useEffect, useState } from "react";
import api from "../api";
import MatchCard from "../components/MatchCard";

export default function Dashboard() {
  const [data, setData] = useState(null);

  useEffect(() => {
    api.get("/matches").then(r => setData(r.data)).catch(() => setData({ status: "waiting", matches: [] }));
  }, []);

  if (!data) return <div className="p-16 text-center text-[#8A6B72]">Aligning...</div>;

  const matches = data.matches || [];
  const high = matches.filter(m => m.score >= 18);
  const low = matches.filter(m => m.score < 18);

  return (
    <div className="min-h-[calc(100vh-4rem)] px-6 md:px-10 py-12 max-w-7xl mx-auto" data-testid="dashboard">
      <div className="mb-12">
        <p className="text-xs tracking-[0.3em] uppercase text-[#D4AF37] mb-3">Your constellation</p>
        <h1 className="font-serif text-4xl sm:text-5xl text-[#F3E6C6]">Compatibility Atlas</h1>
        <div className="flex flex-wrap gap-6 mt-6 text-sm text-[#C2A3A8]">
          <Stat label="Total members" value={matches.length} />
          <Stat label="High compatibility" value={high.length} />
          <Stat label="Casual" value={low.length} />
        </div>
      </div>

      {matches.length === 0 ? (
        <p className="text-[#8A6B72] italic">No members match your preference yet — the cohort will grow as the founding circle expands.</p>
      ) : (
        <>
          {high.length > 0 && (
            <section className="mb-16">
              <div className="flex items-center justify-between mb-6">
                <h2 className="font-serif text-3xl text-[#F3E6C6]">High compatibility</h2>
                <span className="text-xs uppercase tracking-[0.2em] text-[#D4AF37]">Score ≥ 18 / 36</span>
              </div>
              <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
                {high.map(m => <MatchCard key={m.match_user_id} match={m} />)}
              </div>
            </section>
          )}

          {low.length > 0 && (
            <section>
              <div className="flex items-center justify-between mb-6">
                <h2 className="font-serif text-3xl text-[#F3E6C6]">Casual matches</h2>
                <span className="text-xs uppercase tracking-[0.2em] text-[#8A6B72]">Score &lt; 18 / 36</span>
              </div>
              <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
                {low.map(m => <MatchCard key={m.match_user_id} match={m} />)}
              </div>
            </section>
          )}
        </>
      )}
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
