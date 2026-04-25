import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import api, { API, formatApiError } from "../api";
import { DownloadSimple, Warning, Phone, CheckCircle, Clock, XCircle } from "@phosphor-icons/react";
import { toast } from "sonner";

export default function Kundali() {
  const { matchId } = useParams();
  const [data, setData] = useState(null);
  const [err, setErr] = useState("");
  const [requesting, setRequesting] = useState(false);

  const load = () => {
    api.get(`/kundali/${matchId}`).then(r => setData(r.data))
      .catch(e => setErr(formatApiError(e)));
  };

  useEffect(() => { load(); /* eslint-disable-next-line */ }, [matchId]);

  const requestPhone = async () => {
    setRequesting(true);
    try {
      const { data: r } = await api.post("/phone-requests", { receiver_user_id: matchId });
      toast.success(`Request ${r.status === 'pending' ? 'sent' : r.status}.`);
      load();
    } catch (e) { toast.error(formatApiError(e)); } finally { setRequesting(false); }
  };

  if (err) return (
    <div className="p-16 text-center">
      <Warning size={32} className="mx-auto text-[#D4AF37] mb-4" />
      <p className="text-[#C2A3A8]">{err}</p>
      <Link to="/dashboard" className="text-[#D4AF37] underline mt-4 inline-block">← Dashboard</Link>
    </div>
  );
  if (!data) return <div className="p-16 text-center text-[#8A6B72]">Weaving chart...</div>;

  const { match, report, phone_status, phone } = data;
  const pdfUrl = `${API}/kundali/${matchId}/pdf`;

  return (
    <div className="min-h-[calc(100vh-4rem)] px-6 md:px-10 py-12 max-w-5xl mx-auto" data-testid="kundali-report">
      <Link to="/dashboard" className="text-xs tracking-[0.2em] uppercase text-[#8A6B72] hover:text-[#D4AF37]">← Dashboard</Link>

      <div className="mt-6 mb-10 flex flex-wrap gap-6 items-end justify-between">
        <div>
          <p className="text-xs tracking-[0.3em] uppercase text-[#D4AF37] mb-2">Horoscope Matching</p>
          <h1 className="font-serif text-5xl text-[#F3E6C6]">{report.title}</h1>
        </div>
        <a href={pdfUrl} target="_blank" rel="noreferrer" data-testid="download-pdf-button"
          className="flex items-center gap-2 px-5 py-2.5 bg-[#D4AF37] text-[#0A0305] uppercase tracking-[0.2em] text-xs hover:bg-[#B88A2A]">
          <DownloadSimple size={16} /> Download PDF
        </a>
      </div>

      {/* Intro paragraph - per AstroSage format */}
      <div className="p-8 bg-[#1A0810]/80 border border-[#D4AF37]/15 mb-10">
        <p className="text-[#C2A3A8] leading-relaxed">
          Vedic Astrology has an excellent and proven method of compatibility matching based on nakshatras (Lunar Constellations), which is called Ashtakoot match or simply guna milap. It assigns points for factors that influence marriage. More the points obtained, more the chances of successful and happy married life. As the name suggests, maximum possible points are 36. If a matching obtains less than 18 points, it is not considered good and marriage is not advisable. Apart from 36 Points, this report also considers Mangal Dosha (Manglik or Kuja Dosham) compatibility and pronounces results by combining these two important factors.
        </p>
      </div>

      {/* Birth Details Table */}
      <Section title="Birth Details">
        <div className="overflow-x-auto border border-[#D4AF37]/15 bg-[#1A0810]" data-testid="birth-details-table">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-[#7A1E2C]/30 border-b border-[#D4AF37]/20">
                <th className="text-left py-3 px-4 text-xs tracking-[0.2em] uppercase text-[#D4AF37] font-medium">Field</th>
                <th className="text-left py-3 px-4 text-xs tracking-[0.2em] uppercase text-[#D4AF37] font-medium">{report.title.split(" between ")[1]?.split(" and ")[0] || "You"}</th>
                <th className="text-left py-3 px-4 text-xs tracking-[0.2em] uppercase text-[#D4AF37] font-medium">{report.title.split(" and ")[1] || "Partner"}</th>
              </tr>
            </thead>
            <tbody>
              {report.birth_details.map((row, i) => (
                <tr key={row.label} className={`border-b border-[#D4AF37]/5 ${i % 2 ? 'bg-[#0A0305]/30' : ''}`}>
                  <td className="py-3 px-4 text-[#8A6B72] uppercase tracking-[0.15em] text-xs">{row.label}</td>
                  <td className="py-3 px-4 text-[#F3E6C6]">{row.a || "—"}</td>
                  <td className="py-3 px-4 text-[#F3E6C6]">{row.b || "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Section>

      {/* Ashtakoota Points Table */}
      <Section title="Ashtakoota Points Table">
        <div className="overflow-x-auto border border-[#D4AF37]/15 bg-[#1A0810]" data-testid="ashtakoota-table">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-[#7A1E2C]/30 border-b border-[#D4AF37]/20">
                {["Guna","Boy","Girl","Max Points","Points Obtained","Area of Life"].map(h => (
                  <th key={h} className="text-left py-3 px-4 text-xs tracking-[0.2em] uppercase text-[#D4AF37] font-medium">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {report.ashtakoota_table.map((r, i) => (
                <tr key={r.guna} className={`border-b border-[#D4AF37]/5 ${i % 2 ? 'bg-[#0A0305]/30' : ''}`}>
                  <td className="py-3 px-4 text-[#F3E6C6] font-medium uppercase tracking-wide">{r.guna}</td>
                  <td className="py-3 px-4 text-[#C2A3A8]">{r.boy}</td>
                  <td className="py-3 px-4 text-[#C2A3A8]">{r.girl}</td>
                  <td className="py-3 px-4 font-mono text-[#8A6B72]">{r.max_points}</td>
                  <td className="py-3 px-4 font-mono text-[#D4AF37] font-bold">{r.points_obtained}</td>
                  <td className="py-3 px-4 text-[#C2A3A8] italic">{r.area_of_life}</td>
                </tr>
              ))}
              <tr className="bg-[#7A1E2C]/40 border-t-2 border-[#D4AF37]/40">
                <td colSpan={3} className="py-4 px-4 font-serif text-xl text-[#F3E6C6]">Total Match Points Obtained</td>
                <td className="py-4 px-4 font-mono text-[#8A6B72]">36</td>
                <td className="py-4 px-4 font-mono text-2xl text-[#D4AF37] font-bold">{report.total_points}</td>
                <td />
              </tr>
            </tbody>
          </table>
        </div>
      </Section>

      {/* Mangal Dosha */}
      <Section title="Mangal Dosha / Kuja Dosham">
        <div className="p-6 bg-[#1A0810] border border-[#D4AF37]/15" data-testid="mangal-dosha">
          <p className="text-[#F3E6C6] leading-relaxed">{report.mangal_dosha_text}</p>
        </div>
      </Section>

      {/* Conclusion */}
      <Section title="Conclusion">
        <div className="p-8 bg-gradient-to-br from-[#7A1E2C]/40 to-[#2A0E18] border border-[#D4AF37]/30 text-center" data-testid="conclusion">
          <p className="font-serif text-2xl sm:text-3xl text-[#F3E6C6] leading-snug">{report.conclusion_text}</p>
        </div>
      </Section>

      {/* Phone request */}
      <Section title="Phone Number">
        <div className="p-6 bg-[#1A0810] border border-[#D4AF37]/15" data-testid="phone-request-section">
          {phone_status === "accepted" && phone ? (
            <div className="flex items-center gap-3">
              <CheckCircle size={22} weight="duotone" className="text-[#D4AF37]" />
              <p className="text-[#F3E6C6]">Phone access granted: <span className="font-mono">{phone}</span></p>
            </div>
          ) : phone_status === "pending" ? (
            <div className="flex items-center gap-3">
              <Clock size={22} weight="duotone" className="text-[#C2A3A8]" />
              <p className="text-[#C2A3A8]">Your request is pending {match.match_name}'s consent.</p>
            </div>
          ) : phone_status === "rejected" ? (
            <div className="flex items-center gap-3">
              <XCircle size={22} weight="duotone" className="text-[#8A6B72]" />
              <p className="text-[#C2A3A8]">{match.match_name} has chosen not to share their phone number.</p>
            </div>
          ) : (
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
              <div>
                <p className="text-[#F3E6C6] mb-1">Want to take this further?</p>
                <p className="text-xs text-[#8A6B72] italic max-w-xl">
                  Sharing your phone number is completely your personal choice and happens only with your consent.
                </p>
              </div>
              <button onClick={requestPhone} disabled={requesting} data-testid="request-phone-button"
                className="flex items-center gap-2 px-5 py-2.5 bg-[#D4AF37] text-[#0A0305] uppercase tracking-[0.2em] text-xs hover:bg-[#B88A2A] disabled:opacity-60 whitespace-nowrap">
                <Phone size={16} /> Request phone number
              </button>
            </div>
          )}
        </div>
      </Section>

      {/* Interpretations */}
      <Section title="Interpretation of Each Point">
        <div className="space-y-6" data-testid="interpretations">
          {report.interpretations.map(({ guna, text }) => (
            <article key={guna} className="p-6 bg-[#1A0810] border-l-2 border-[#D4AF37]/40">
              <h3 className="font-serif text-2xl text-[#D4AF37] mb-3 uppercase tracking-wider">{guna}</h3>
              <p className="text-[#C2A3A8] leading-relaxed">{text}</p>
            </article>
          ))}
        </div>
      </Section>

      <div className="mt-12 p-6 bg-[#0A0305]/60 border border-[#D4AF37]/10 text-xs text-[#8A6B72] leading-relaxed" data-testid="disclaimer">
        <p className="uppercase tracking-[0.2em] text-[#D4AF37] mb-2">Disclaimer</p>
        <p>We put our best efforts into this report but any prediction received is not a substitute for advice from a licensed professional such as a doctor, lawyer, financial adviser or psychiatrist. While calculations are made carefully, errors are possible. The report is provided as-is with no implied warranties.</p>
      </div>
    </div>
  );
}

function Section({ title, children }) {
  return (
    <section className="mb-12">
      <h2 className="font-serif text-3xl text-[#F3E6C6] mb-6 pb-3 border-b border-[#D4AF37]/15">{title}</h2>
      {children}
    </section>
  );
}
