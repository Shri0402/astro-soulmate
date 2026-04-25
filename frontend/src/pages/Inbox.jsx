import { useEffect, useState } from "react";
import api, { formatApiError } from "../api";
import { CheckCircle, XCircle, Clock } from "@phosphor-icons/react";
import { toast } from "sonner";

export default function Inbox() {
  const [tab, setTab] = useState("inbox");
  const [inbox, setInbox] = useState([]);
  const [sent, setSent] = useState([]);
  const load = async () => {
    try {
      const [a, b] = await Promise.all([api.get("/phone-requests/inbox"), api.get("/phone-requests/sent")]);
      setInbox(a.data.items || []); setSent(b.data.items || []);
    } catch {}
  };
  useEffect(() => { load(); }, []);

  const act = async (id, action) => {
    try {
      await api.post(`/phone-requests/${id}/${action}`);
      toast.success(`Request ${action}ed.`);
      load();
    } catch (e) { toast.error(formatApiError(e)); }
  };

  return (
    <div className="min-h-[calc(100vh-4rem)] px-6 md:px-10 py-12 max-w-4xl mx-auto" data-testid="inbox-page">
      <p className="text-xs tracking-[0.3em] uppercase text-[#D4AF37] mb-2">Notifications</p>
      <h1 className="font-serif text-4xl text-[#F3E6C6] mb-8">Phone access requests</h1>

      <div className="flex gap-1 mb-6">
        {[["inbox", `Inbox (${inbox.filter(i => i.status === 'pending').length})`], ["sent", "Sent"]].map(([k, l]) => (
          <button key={k} onClick={() => setTab(k)} data-testid={`inbox-tab-${k}`}
            className={`px-5 py-2 text-xs uppercase tracking-[0.2em] border ${tab === k ? 'bg-[#D4AF37] text-[#0A0305] border-[#D4AF37]' : 'border-[#D4AF37]/20 text-[#C2A3A8]'}`}>{l}</button>
        ))}
      </div>

      {tab === "inbox" ? (
        inbox.length === 0 ? <Empty>No incoming requests.</Empty> : (
          <ul className="space-y-3">
            {inbox.map(it => (
              <li key={it.id} className="p-5 bg-[#1A0810] border border-[#D4AF37]/15 flex items-center gap-4" data-testid={`inbox-item-${it.id}`}>
                <Status s={it.status} />
                <div className="flex-1 min-w-0">
                  <p className="text-[#F3E6C6]"><strong>{it.requester_name}</strong> wants access to your phone number.</p>
                  <p className="text-xs text-[#8A6B72] mt-1">{new Date(it.created_at).toLocaleString()}</p>
                </div>
                {it.status === "pending" && (
                  <div className="flex gap-2">
                    <button onClick={() => act(it.id, "accept")} data-testid={`accept-${it.id}`}
                      className="px-4 py-2 bg-[#D4AF37] text-[#0A0305] uppercase tracking-[0.2em] text-[10px] hover:bg-[#B88A2A]">Accept</button>
                    <button onClick={() => act(it.id, "reject")} data-testid={`reject-${it.id}`}
                      className="px-4 py-2 border border-[#D4AF37]/30 text-[#C2A3A8] uppercase tracking-[0.2em] text-[10px] hover:border-[#E87B7B]">Decline</button>
                  </div>
                )}
              </li>
            ))}
          </ul>
        )
      ) : (
        sent.length === 0 ? <Empty>No outgoing requests.</Empty> : (
          <ul className="space-y-3">
            {sent.map(it => (
              <li key={it.id} className="p-5 bg-[#1A0810] border border-[#D4AF37]/15 flex items-center gap-4">
                <Status s={it.status} />
                <div className="flex-1">
                  <p className="text-[#F3E6C6]">You requested <strong>{it.receiver_name}</strong>'s phone number.</p>
                  <p className="text-xs text-[#8A6B72] mt-1">{new Date(it.created_at).toLocaleString()} · {it.status}</p>
                </div>
              </li>
            ))}
          </ul>
        )
      )}
    </div>
  );
}

function Empty({ children }) {
  return <p className="text-center text-[#8A6B72] italic py-12">{children}</p>;
}
function Status({ s }) {
  if (s === "accepted") return <CheckCircle size={28} weight="duotone" className="text-[#D4AF37]" />;
  if (s === "rejected") return <XCircle size={28} weight="duotone" className="text-[#8A6B72]" />;
  return <Clock size={28} weight="duotone" className="text-[#C2A3A8]" />;
}
