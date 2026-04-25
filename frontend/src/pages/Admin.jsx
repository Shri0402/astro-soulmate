import { useEffect, useState } from "react";
import api, { formatApiError } from "../api";
import { useAuth } from "../context/AuthContext";
import { CheckCircle, XCircle } from "@phosphor-icons/react";
import { toast } from "sonner";

export default function Admin() {
  const { user } = useAuth();
  const [requests, setRequests] = useState([]);
  const [members, setMembers] = useState([]);
  const [tab, setTab] = useState("requests");

  const load = () => {
    api.get("/admin/change-requests?status=pending").then(r => setRequests(r.data.items || [])).catch(() => {});
    api.get("/admin/members").then(r => setMembers(r.data.items || [])).catch(() => {});
  };
  useEffect(() => { load(); }, []);

  const decide = async (id, action) => {
    try {
      await api.post(`/admin/change-requests/${id}/${action}`);
      toast.success(`Request ${action}d`);
      load();
    } catch (e) { toast.error(formatApiError(e)); }
  };

  if (!user || user.role !== "admin") {
    return <div className="p-16 text-center text-[#8A6B72]">Admin only.</div>;
  }

  return (
    <div className="min-h-[calc(100vh-4rem)] px-6 md:px-10 py-12 max-w-6xl mx-auto" data-testid="admin-page">
      <p className="text-xs tracking-[0.3em] uppercase text-[#D4AF37] mb-2">Council</p>
      <h1 className="font-serif text-4xl text-[#F3E6C6] mb-8">Admin</h1>

      <div className="flex gap-1 mb-6">
        {[["requests", `Pending requests (${requests.length})`], ["members", `Members (${members.length})`]].map(([k,l]) => (
          <button key={k} onClick={() => setTab(k)} data-testid={`admin-tab-${k}`}
            className={`px-5 py-2 text-xs uppercase tracking-[0.2em] border ${tab === k ? 'bg-[#D4AF37] text-[#0A0305] border-[#D4AF37]' : 'border-[#D4AF37]/20 text-[#C2A3A8]'}`}>{l}</button>
        ))}
      </div>

      {tab === "requests" ? (
        requests.length === 0 ? (
          <p className="text-center text-[#8A6B72] italic py-12">No pending requests.</p>
        ) : (
          <ul className="space-y-3">
            {requests.map(r => (
              <li key={r.id} className="p-5 bg-[#1A0810] border border-[#D4AF37]/15" data-testid={`request-${r.id}`}>
                <div className="flex flex-wrap gap-4 items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <p className="text-[#F3E6C6]"><strong>{r.user_name}</strong> ({r.user_email})</p>
                    <p className="text-sm text-[#C2A3A8] mt-1">
                      Wants to change <strong className="text-[#D4AF37]">{r.field}</strong>: <span className="text-[#8A6B72] line-through">{String(r.old_value || "—")}</span> → <span className="text-[#D4AF37]">{r.new_value}</span>
                    </p>
                    {r.reason && <p className="text-xs text-[#8A6B72] mt-2 italic">"{r.reason}"</p>}
                    <p className="text-xs text-[#8A6B72] mt-2">{new Date(r.created_at).toLocaleString()}</p>
                  </div>
                  <div className="flex gap-2">
                    <button onClick={() => decide(r.id, "approve")} data-testid={`approve-${r.id}`}
                      className="flex items-center gap-1.5 px-4 py-2 bg-[#D4AF37] text-[#0A0305] uppercase tracking-[0.2em] text-[10px] hover:bg-[#B88A2A]">
                      <CheckCircle size={14} /> Approve
                    </button>
                    <button onClick={() => decide(r.id, "reject")} data-testid={`reject-req-${r.id}`}
                      className="flex items-center gap-1.5 px-4 py-2 border border-[#D4AF37]/30 text-[#C2A3A8] uppercase tracking-[0.2em] text-[10px] hover:border-[#E87B7B]">
                      <XCircle size={14} /> Reject
                    </button>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        )
      ) : (
        <div className="overflow-x-auto border border-[#D4AF37]/15 bg-[#1A0810]">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-[#7A1E2C]/30 border-b border-[#D4AF37]/20">
                {["Name","Email","Gender","Looking","City","Joined"].map(h => (
                  <th key={h} className="text-left py-3 px-4 text-xs tracking-[0.2em] uppercase text-[#D4AF37] font-medium">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {members.map((m, i) => (
                <tr key={m._id} className={`border-b border-[#D4AF37]/5 ${i % 2 ? 'bg-[#0A0305]/30' : ''}`} data-testid={`member-${m._id}`}>
                  <td className="py-3 px-4 text-[#F3E6C6]">{m.name || m.full_name || "—"}</td>
                  <td className="py-3 px-4 text-[#C2A3A8] text-xs">{m.email}</td>
                  <td className="py-3 px-4 text-[#C2A3A8]">{m.gender || "—"}</td>
                  <td className="py-3 px-4 text-[#C2A3A8]">{m.looking_for || "—"}</td>
                  <td className="py-3 px-4 text-[#C2A3A8]">{m.city || m.birth_city || "—"}</td>
                  <td className="py-3 px-4 text-[#8A6B72] text-xs">{m.created_at ? new Date(m.created_at).toLocaleDateString() : "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
