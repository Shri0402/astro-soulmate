import { useEffect, useState } from "react";
import api, { formatApiError } from "../api";
import { useAuth } from "../context/AuthContext";
import { Lock, Pencil, Clock, CheckCircle, XCircle } from "@phosphor-icons/react";
import { toast } from "sonner";

const FREE = ["bio", "phone", "birth_city", "state", "name"];
const SENSITIVE = ["looking_for", "dob", "birth_time", "gender"];

export default function Profile() {
  const { user, refreshUser } = useAuth();
  const [free, setFree] = useState({});
  const [requests, setRequests] = useState([]);
  const [chgField, setChgField] = useState("looking_for");
  const [chgValue, setChgValue] = useState("");
  const [chgReason, setChgReason] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (user) {
      setFree({
        name: user.name || "", bio: user.bio || "", phone: user.phone || "",
        birth_city: user.birth_city || "", state: user.state || "",
      });
    }
    api.get("/profile/change-requests/mine").then(r => setRequests(r.data.items || [])).catch(() => {});
  }, [user]);

  const saveFree = async () => {
    setBusy(true);
    try { await api.patch("/profile", free); await refreshUser(); toast.success("Profile updated."); }
    catch (e) { toast.error(formatApiError(e)); } finally { setBusy(false); }
  };

  const submitChange = async () => {
    if (!chgValue) { toast.error("Enter a value."); return; }
    setBusy(true);
    try {
      await api.post("/profile/change-request", { field: chgField, new_value: chgValue, reason: chgReason });
      toast.success("Change request submitted for admin review.");
      setChgValue(""); setChgReason("");
      api.get("/profile/change-requests/mine").then(r => setRequests(r.data.items || []));
    } catch (e) { toast.error(formatApiError(e)); } finally { setBusy(false); }
  };

  if (!user) return null;

  return (
    <div className="min-h-[calc(100vh-4rem)] px-6 md:px-10 py-12 max-w-4xl mx-auto" data-testid="profile-page">
      <p className="text-xs tracking-[0.3em] uppercase text-[#D4AF37] mb-2">Account</p>
      <h1 className="font-serif text-4xl text-[#F3E6C6] mb-2">Profile</h1>
      <p className="text-sm text-[#8A6B72] mb-10">Referred by {user.referred_by_name || "Founding Cohort"}</p>

      {/* Free edit */}
      <Section title="Editable details">
        <div className="p-6 bg-[#1A0810] border border-[#D4AF37]/15 grid sm:grid-cols-2 gap-4">
          {[
            {k:"name", l:"Display name"},
            {k:"phone", l:"Phone (only shared on consent)"},
            {k:"birth_city", l:"City"},
            {k:"state", l:"State"},
          ].map(({k,l}) => (
            <div key={k}>
              <label className="block text-xs tracking-[0.2em] uppercase text-[#8A6B72] mb-2">{l}</label>
              <input value={free[k] || ""} onChange={e => setFree(f => ({...f, [k]: e.target.value}))}
                data-testid={`profile-${k}`}
                className="w-full bg-[#2A0E18] border border-[#D4AF37]/20 px-4 py-3 text-[#F3E6C6] outline-none focus:border-[#D4AF37]" />
            </div>
          ))}
          <div className="sm:col-span-2">
            <label className="block text-xs tracking-[0.2em] uppercase text-[#8A6B72] mb-2">About you</label>
            <textarea rows={3} value={free.bio || ""} onChange={e => setFree(f => ({...f, bio: e.target.value}))}
              data-testid="profile-bio"
              className="w-full bg-[#2A0E18] border border-[#D4AF37]/20 px-4 py-3 text-[#F3E6C6] outline-none focus:border-[#D4AF37]" />
          </div>
          <div className="sm:col-span-2 flex justify-end">
            <button onClick={saveFree} disabled={busy} data-testid="profile-save"
              className="px-6 py-2.5 bg-[#D4AF37] text-[#0A0305] uppercase tracking-[0.2em] text-xs hover:bg-[#B88A2A] disabled:opacity-60">
              <Pencil size={14} className="inline mr-2" /> Save changes
            </button>
          </div>
        </div>
      </Section>

      {/* Frozen / sensitive fields */}
      <Section title="Locked details">
        <div className="p-6 bg-[#1A0810] border border-[#D4AF37]/15">
          <div className="grid sm:grid-cols-2 gap-4 mb-6">
            {[
              {l:"Date of Birth", v:user.dob},
              {l:"Birth Time", v:user.birth_time},
              {l:"Gender", v:user.gender},
              {l:"Looking For", v:user.looking_for},
            ].map(({l,v}) => (
              <div key={l} className="flex items-center justify-between py-3 border-b border-[#D4AF37]/10">
                <div>
                  <p className="text-xs tracking-[0.2em] uppercase text-[#8A6B72]">{l}</p>
                  <p className="text-[#F3E6C6] mt-1">{v || "—"}</p>
                </div>
                <Lock size={18} className="text-[#8A6B72]" />
              </div>
            ))}
          </div>
          <p className="text-xs text-[#8A6B72] italic mb-4">
            DOB and Birth Time form your immutable kundali identity. Other locked fields require admin approval before they change.
          </p>

          <div className="border-t border-[#D4AF37]/10 pt-6">
            <p className="text-xs tracking-[0.3em] uppercase text-[#D4AF37] mb-4">Request a change</p>
            <div className="grid sm:grid-cols-2 gap-3">
              <select value={chgField} onChange={e => setChgField(e.target.value)} data-testid="change-field"
                className="bg-[#2A0E18] border border-[#D4AF37]/20 px-4 py-3 text-[#F3E6C6] outline-none focus:border-[#D4AF37]">
                <option value="looking_for">Looking For</option>
                <option value="gender">Gender</option>
                <option value="dob">Date of Birth (correction)</option>
                <option value="birth_time">Birth Time (correction)</option>
              </select>
              <input value={chgValue} onChange={e => setChgValue(e.target.value)} placeholder="New value"
                data-testid="change-value"
                className="bg-[#2A0E18] border border-[#D4AF37]/20 px-4 py-3 text-[#F3E6C6] outline-none focus:border-[#D4AF37]" />
            </div>
            <textarea value={chgReason} onChange={e => setChgReason(e.target.value)} placeholder="Reason (optional)"
              data-testid="change-reason" rows={2}
              className="w-full mt-3 bg-[#2A0E18] border border-[#D4AF37]/20 px-4 py-3 text-[#F3E6C6] outline-none focus:border-[#D4AF37]" />
            <div className="flex justify-end mt-3">
              <button onClick={submitChange} disabled={busy} data-testid="submit-change-request"
                className="px-6 py-2.5 bg-[#D4AF37] text-[#0A0305] uppercase tracking-[0.2em] text-xs hover:bg-[#B88A2A] disabled:opacity-60">
                Submit request
              </button>
            </div>
          </div>
        </div>
      </Section>

      {requests.length > 0 && (
        <Section title="Your change requests">
          <ul className="space-y-2">
            {requests.map(r => (
              <li key={r.id} className="p-4 bg-[#1A0810] border border-[#D4AF37]/15 flex items-center gap-4 text-sm">
                <StatusIcon s={r.status} />
                <div className="flex-1 min-w-0">
                  <p className="text-[#F3E6C6]"><strong>{r.field}</strong> → <span className="text-[#D4AF37]">{r.new_value}</span></p>
                  <p className="text-xs text-[#8A6B72] mt-0.5">{new Date(r.created_at).toLocaleString()} · {r.status}</p>
                </div>
              </li>
            ))}
          </ul>
        </Section>
      )}
    </div>
  );
}

function Section({ title, children }) {
  return (
    <section className="mb-10">
      <h2 className="font-serif text-2xl text-[#F3E6C6] mb-4">{title}</h2>
      {children}
    </section>
  );
}
function StatusIcon({ s }) {
  if (s === "approved") return <CheckCircle size={22} weight="duotone" className="text-[#D4AF37]" />;
  if (s === "rejected") return <XCircle size={22} weight="duotone" className="text-[#8A6B72]" />;
  return <Clock size={22} weight="duotone" className="text-[#C2A3A8]" />;
}
