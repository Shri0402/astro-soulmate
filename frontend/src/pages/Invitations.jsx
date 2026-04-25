import { useEffect, useState } from "react";
import api, { formatApiError } from "../api";
import { Copy, CheckCircle } from "@phosphor-icons/react";
import { toast } from "sonner";

export default function Invitations() {
  const [items, setItems] = useState([]);
  const [note, setNote] = useState("");
  const [busy, setBusy] = useState(false);

  const load = async () => {
    try { const r = await api.get("/invites/mine"); setItems(r.data.items || []); } catch {}
  };
  useEffect(() => { load(); }, []);

  const create = async () => {
    setBusy(true);
    try { await api.post("/invites", { note }); setNote(""); load(); toast.success("Invite generated."); }
    catch (e) { toast.error(formatApiError(e)); } finally { setBusy(false); }
  };

  const copy = (code) => {
    const url = `${window.location.origin}/invite/${code}`;
    navigator.clipboard.writeText(url);
    toast.success("Invite link copied.");
  };

  return (
    <div className="min-h-[calc(100vh-4rem)] px-6 md:px-10 py-12 max-w-4xl mx-auto" data-testid="invitations-page">
      <p className="text-xs tracking-[0.3em] uppercase text-[#D4AF37] mb-2">Refer a soul</p>
      <h1 className="font-serif text-4xl text-[#F3E6C6] mb-3">Invitations</h1>
      <p className="text-[#C2A3A8] mb-10 max-w-2xl">Stars Connection grows only by referral. Generate an invite, share the link, and welcome a new seeker into the circle.</p>

      <div className="p-6 bg-[#1A0810] border border-[#D4AF37]/15 mb-10">
        <label className="block text-xs tracking-[0.2em] uppercase text-[#8A6B72] mb-2">Note (optional)</label>
        <div className="flex gap-3">
          <input value={note} onChange={e => setNote(e.target.value)} placeholder="e.g. for my cousin Riya"
            className="flex-1 bg-[#2A0E18] border border-[#D4AF37]/20 px-4 py-3 text-[#F3E6C6] outline-none focus:border-[#D4AF37]"
            data-testid="invite-note" />
          <button onClick={create} disabled={busy} data-testid="generate-invite"
            className="px-6 py-3 bg-[#D4AF37] text-[#0A0305] uppercase tracking-[0.2em] text-xs hover:bg-[#B88A2A] disabled:opacity-60 whitespace-nowrap">
            Generate invite
          </button>
        </div>
      </div>

      <ul className="space-y-3">
        {items.length === 0 ? (
          <p className="text-center text-[#8A6B72] italic py-8">You haven't generated any invites yet.</p>
        ) : items.map(i => (
          <li key={i.code} className="p-5 bg-[#1A0810] border border-[#D4AF37]/15 flex items-center gap-4" data-testid={`invite-${i.code}`}>
            <div className="flex-1 min-w-0">
              <code className="font-mono text-lg text-[#D4AF37] tracking-widest">{i.code}</code>
              {i.note && <p className="text-xs text-[#C2A3A8] mt-1">{i.note}</p>}
              <p className="text-xs text-[#8A6B72] mt-1">{new Date(i.created_at).toLocaleString()}</p>
            </div>
            {i.used ? (
              <span className="flex items-center gap-1.5 text-xs uppercase tracking-[0.2em] text-[#8A6B72]"><CheckCircle size={14} /> Accepted</span>
            ) : (
              <button onClick={() => copy(i.code)} data-testid={`copy-${i.code}`}
                className="flex items-center gap-1.5 px-4 py-2 border border-[#D4AF37]/30 text-[#C2A3A8] uppercase tracking-[0.2em] text-[10px] hover:border-[#D4AF37] hover:text-[#D4AF37]">
                <Copy size={14} /> Copy link
              </button>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}
