import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import api, { API } from "../api";
import { DownloadSimple, Warning } from "@phosphor-icons/react";

const DESCRIPTIONS = {
  Varna: "Spiritual & work compatibility — ego alignment.",
  Vashya: "Mutual attraction & willingness to yield.",
  Tara: "Health & overall well-being of the union.",
  Yoni: "Physical & sexual compatibility.",
  "Graha Maitri": "Mental & psychological bond of the rashi lords.",
  Gana: "Temperament: divine, human, or demonic.",
  Bhakoot: "Wealth, family welfare & prosperity.",
  Nadi: "Genetic & health compatibility — most critical guna.",
};

export default function Kundali() {
  const { matchId } = useParams();
  const [data, setData] = useState(null);
  const [err, setErr] = useState("");

  useEffect(() => {
    api.get(`/kundali/${matchId}`)
      .then(r => setData(r.data))
      .catch(e => setErr(e.response?.data?.detail || "Unable to load."));
  }, [matchId]);

  if (err) return (
    <div className="p-16 text-center">
      <Warning size={32} className="mx-auto text-[#D4AF37] mb-4" />
      <p className="text-[#C2A3A8]">{String(err)}</p>
      <Link to="/dashboard" className="text-[#D4AF37] underline mt-4 inline-block">← Back to dashboard</Link>
    </div>
  );
  if (!data) return <div className="p-16 text-center text-[#8A6B72]">Weaving chart...</div>;

  const { match, self } = data;
  const pdfUrl = `${API}/kundali/${matchId}/pdf`;

  return (
    <div className="min-h-[calc(100vh-4rem)] px-6 md:px-10 py-12 max-w-5xl mx-auto" data-testid="kundali-report">
      <Link to="/dashboard" className="text-xs tracking-[0.2em] uppercase text-[#8A6B72] hover:text-[#D4AF37]">← Dashboard</Link>
      <div className="mt-6 mb-10 flex flex-wrap gap-6 items-end justify-between">
        <div>
          <p className="text-xs tracking-[0.3em] uppercase text-[#D4AF37] mb-2">Compatibility report</p>
          <h1 className="font-serif text-5xl text-[#F3E6C6]">{self.name} &amp; {match.match_name}</h1>
        </div>
        <a href={pdfUrl} target="_blank" rel="noreferrer" data-testid="download-pdf-button"
          className="flex items-center gap-2 px-5 py-2.5 bg-[#D4AF37] text-[#0A0305] uppercase tracking-[0.2em] text-xs hover:bg-[#B88A2A]">
          <DownloadSimple size={16} /> PDF report
        </a>
      </div>

      {/* Score Summary */}
      <div className="p-10 bg-gradient-to-br from-[#2A0E18] to-[#1A0810] border border-[#D4AF37]/25 text-center mb-10">
        <p className="text-xs tracking-[0.3em] uppercase text-[#8A6B72] mb-4">Ashtakoota score</p>
        <p className="font-serif text-7xl text-[#D4AF37] leading-none">{match.score}<span className="text-[#8A6B72] text-3xl"> / 36</span></p>
        <p className="text-[#C2A3A8] mt-6 max-w-2xl mx-auto leading-relaxed">{match.verdict}</p>
      </div>

      {/* Birth details */}
      <section className="mb-12">
        <h2 className="font-serif text-3xl text-[#F3E6C6] mb-6">Birth details</h2>
        <div className="grid md:grid-cols-2 gap-6">
          <DetailTable title={self.name} rows={[
            ["Gender", self.gender], ["DOB", self.dob], ["Birth city", self.birth_city],
            ["Rashi", self.astro?.rashi], ["Nakshatra", `${self.astro?.nakshatra} (Pada ${self.astro?.pada})`],
          ]} />
          <DetailTable title={match.match_name} rows={[
            ["Gender", match.match_gender], ["DOB", match.match_dob], ["Birth city", match.match_city],
            ["Mangal Dosha (You)", match.mangal_a ? "Present" : "Absent"],
            ["Mangal Dosha (Partner)", match.mangal_b ? "Present" : "Absent"],
          ]} />
        </div>
      </section>

      {/* Guna breakdown */}
      <section className="mb-12">
        <h2 className="font-serif text-3xl text-[#F3E6C6] mb-6">8 Gunas</h2>
        <div className="space-y-3">
          {Object.entries(match.breakdown).map(([name, g]) => (
            <div key={name} className="p-5 bg-[#1A0810] border border-[#D4AF37]/10" data-testid={`guna-${name.replace(' ', '-')}`}>
              <div className="flex items-baseline justify-between mb-2">
                <div>
                  <h3 className="font-serif text-xl text-[#F3E6C6]">{name}</h3>
                  <p className="text-xs text-[#8A6B72] mt-0.5">{DESCRIPTIONS[name]}</p>
                </div>
                <span className="font-mono text-lg text-[#D4AF37]">{g.score} / {g.max}</span>
              </div>
              <div className="h-1.5 bg-[#2A0E18] overflow-hidden">
                <div className="h-full bg-[#D4AF37]" style={{ width: `${(g.score / g.max) * 100}%` }} />
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

function DetailTable({ title, rows }) {
  return (
    <div className="p-6 bg-[#1A0810] border border-[#D4AF37]/15">
      <h3 className="font-serif text-2xl text-[#F3E6C6] mb-4 pb-3 border-b border-[#D4AF37]/10">{title}</h3>
      <dl className="space-y-3">
        {rows.map(([k, v]) => (
          <div key={k} className="flex justify-between text-sm">
            <dt className="text-[#8A6B72] uppercase tracking-[0.15em] text-xs">{k}</dt>
            <dd className="text-[#F3E6C6]">{v || "—"}</dd>
          </div>
        ))}
      </dl>
    </div>
  );
}
