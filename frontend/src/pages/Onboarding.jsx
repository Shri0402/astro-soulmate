import { useState } from "react";
import { useNavigate } from "react-router-dom";
import api, { formatApiError } from "../api";
import { useAuth } from "../context/AuthContext";

const CITIES = ["Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata", "Hyderabad", "Pune",
  "Ahmedabad", "Jaipur", "Lucknow", "Chandigarh", "Bhopal", "Indore", "Patna", "Nagpur",
  "Surat", "Kochi", "Thiruvananthapuram", "Varanasi", "Amritsar", "New York", "London", "Dubai", "Singapore", "Toronto", "Sydney"];

export default function Onboarding() {
  const { refreshUser, user } = useAuth();
  const nav = useNavigate();
  const [step, setStep] = useState(1);
  const [form, setForm] = useState({
    name: user?.name || "",
    gender: "", looking_for: "",
    dob: "", birth_time: "", birth_city: "Mumbai", bio: "",
  });
  const [err, setErr] = useState(""); const [loading, setLoading] = useState(false);
  const up = (k, v) => setForm(f => ({ ...f, [k]: v }));

  const submit = async () => {
    setErr(""); setLoading(true);
    try {
      const { data } = await api.post("/profile", form);
      await refreshUser();
      if (data.matches_generated > 0) nav("/dashboard");
      else nav("/waiting");
    } catch (e) { setErr(formatApiError(e)); } finally { setLoading(false); }
  };

  return (
    <div className="min-h-[calc(100vh-4rem)] starfield px-6 py-16">
      <div className="max-w-2xl mx-auto">
        <p className="text-xs tracking-[0.3em] uppercase text-[#D4AF37] mb-3">Step {step} of 3</p>
        <h1 className="font-serif text-4xl sm:text-5xl text-[#F3E6C6] mb-3">Tell the stars about you</h1>
        <p className="text-[#C2A3A8] mb-10">Your chart is computed the moment you complete this. Accuracy of birth time matters.</p>

        <div className="p-8 bg-[#1A0810]/80 border border-[#D4AF37]/20 backdrop-blur-md" data-testid="onboarding-form">
          {step === 1 && (
            <>
              <L label="Your name">
                <I value={form.name} onChange={v => up("name", v)} testid="ob-name" />
              </L>
              <L label="You are">
                <div className="flex gap-3">
                  {["female", "male"].map(g => (
                    <button key={g} type="button" onClick={() => up("gender", g)} data-testid={`ob-gender-${g}`}
                      className={`flex-1 py-3 border ${form.gender === g ? 'border-[#D4AF37] bg-[#2A0E18] text-[#D4AF37]' : 'border-[#D4AF37]/20 text-[#C2A3A8]'} uppercase tracking-[0.2em] text-xs`}>
                      {g}
                    </button>
                  ))}
                </div>
              </L>
              <L label="Looking for">
                <div className="flex gap-3">
                  {["female", "male"].map(g => (
                    <button key={g} type="button" onClick={() => up("looking_for", g)} data-testid={`ob-looking-${g}`}
                      className={`flex-1 py-3 border ${form.looking_for === g ? 'border-[#D4AF37] bg-[#2A0E18] text-[#D4AF37]' : 'border-[#D4AF37]/20 text-[#C2A3A8]'} uppercase tracking-[0.2em] text-xs`}>
                      {g}
                    </button>
                  ))}
                </div>
              </L>
            </>
          )}
          {step === 2 && (
            <>
              <L label="Date of birth">
                <I type="date" value={form.dob} onChange={v => up("dob", v)} testid="ob-dob" />
              </L>
              <L label="Exact birth time (24h)">
                <I type="time" value={form.birth_time} onChange={v => up("birth_time", v)} testid="ob-time" />
              </L>
              <L label="Birth city">
                <select value={form.birth_city} onChange={e => up("birth_city", e.target.value)} data-testid="ob-city"
                  className="w-full bg-[#2A0E18] border border-[#D4AF37]/20 px-4 py-3 text-[#F3E6C6] outline-none focus:border-[#D4AF37]">
                  {CITIES.map(c => <option key={c}>{c}</option>)}
                </select>
              </L>
            </>
          )}
          {step === 3 && (
            <>
              <L label="A short note about yourself">
                <textarea value={form.bio} onChange={e => up("bio", e.target.value)} data-testid="ob-bio" rows={4}
                  className="w-full bg-[#2A0E18] border border-[#D4AF37]/20 px-4 py-3 text-[#F3E6C6] outline-none focus:border-[#D4AF37]" />
              </L>
              <div className="text-sm text-[#8A6B72] p-4 bg-[#0A0305]/50 border-l-2 border-[#D4AF37]">
                <strong className="text-[#D4AF37] uppercase tracking-[0.2em] text-xs">Note</strong>
                <p className="mt-2">We will compute your Moon sign, Nakshatra, Rashi, and prepare your Ashtakoota compatibility engine. This is irreversible without support — please verify accuracy.</p>
              </div>
            </>
          )}
          {err && <p className="text-sm text-[#E87B7B] mt-4">{err}</p>}
          <div className="flex justify-between mt-8">
            <button type="button" disabled={step === 1} onClick={() => setStep(s => s - 1)} data-testid="ob-back"
              className="px-6 py-2.5 border border-[#D4AF37]/30 text-[#C2A3A8] uppercase tracking-[0.2em] text-xs disabled:opacity-30">Back</button>
            {step < 3 ? (
              <button type="button" onClick={() => setStep(s => s + 1)} data-testid="ob-next"
                disabled={step === 1 && (!form.name || !form.gender || !form.looking_for) || step === 2 && (!form.dob || !form.birth_time)}
                className="px-8 py-2.5 bg-[#D4AF37] text-[#0A0305] uppercase tracking-[0.2em] text-xs hover:bg-[#B88A2A] disabled:opacity-40">Continue</button>
            ) : (
              <button type="button" disabled={loading} onClick={submit} data-testid="ob-submit"
                className="px-8 py-2.5 bg-[#D4AF37] text-[#0A0305] uppercase tracking-[0.2em] text-xs hover:bg-[#B88A2A] disabled:opacity-60">
                {loading ? "Computing..." : "Cast my chart"}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function L({ label, children }) {
  return (
    <div className="mb-6">
      <label className="block text-xs tracking-[0.2em] uppercase text-[#8A6B72] mb-2">{label}</label>
      {children}
    </div>
  );
}
function I({ value, onChange, type = "text", testid }) {
  return (
    <input type={type} required value={value} onChange={e => onChange(e.target.value)} data-testid={testid}
      className="w-full bg-[#2A0E18] border border-[#D4AF37]/20 px-4 py-3 text-[#F3E6C6] outline-none focus:border-[#D4AF37]" />
  );
}
