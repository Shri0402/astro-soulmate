import { Link, useNavigate, useLocation } from "react-router-dom";
import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import api from "../api";
import { Star, SignOut, Bell, Envelope, Users, User, Crown } from "@phosphor-icons/react";

export default function Navbar() {
  const { user, logout } = useAuth();
  const nav = useNavigate();
  const loc = useLocation();
  const [pending, setPending] = useState(0);

  useEffect(() => {
    if (!user) return;
    let stop = false;
    const tick = async () => {
      try { const { data } = await api.get("/phone-requests/inbox"); if (!stop) setPending(data.pending_count || 0); } catch {}
    };
    tick();
    const iv = setInterval(tick, 20000);
    return () => { stop = true; clearInterval(iv); };
  }, [user, loc.pathname]);

  const handleLogout = async () => { await logout(); nav("/"); };
  const link = (path, txt, testid, Icon, badge=0) => (
    <Link to={path} data-testid={testid} className={`relative flex items-center gap-1.5 hover:text-[#D4AF37] transition ${loc.pathname === path ? 'text-[#D4AF37]' : ''}`}>
      {Icon && <Icon size={16} />} {txt}
      {badge > 0 && <span className="absolute -top-2 -right-3 min-w-[18px] h-[18px] px-1 rounded-full bg-[#D4AF37] text-[#0A0305] text-[10px] font-bold flex items-center justify-center">{badge}</span>}
    </Link>
  );

  return (
    <header className="relative z-20 border-b border-[#D4AF37]/10 bg-[#0A0305]/70 backdrop-blur-xl">
      <div className="max-w-7xl mx-auto px-6 md:px-10 h-16 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2 group" data-testid="navbar-logo">
          <Star weight="fill" size={22} className="text-[#D4AF37] group-hover:rotate-12 transition-transform" />
          <span className="font-serif text-xl text-[#F3E6C6] tracking-wide">Stars Connection</span>
        </Link>
        <nav className="flex items-center gap-5 text-sm text-[#C2A3A8]">
          {user ? (
            <>
              {user.profile_complete && link("/dashboard", "Dashboard", "nav-dashboard")}
              {user.profile_complete && link("/inbox", "", "nav-inbox", Bell, pending)}
              {user.profile_complete && link("/invitations", "", "nav-invites", Users)}
              {user.profile_complete && link("/profile", "", "nav-profile", User)}
              {user.role === "admin" && link("/admin", "Admin", "nav-admin", Crown)}
              <span className="hidden sm:inline text-[#8A6B72]">{user.name}</span>
              <button onClick={handleLogout} data-testid="nav-logout"
                className="flex items-center gap-1.5 px-3 py-1.5 border border-[#D4AF37]/30 hover:border-[#D4AF37] hover:text-[#D4AF37] transition">
                <SignOut size={16} /> Logout
              </button>
            </>
          ) : (
            <Link to="/login" className="hover:text-[#D4AF37] transition" data-testid="nav-login">Member login</Link>
          )}
        </nav>
      </div>
    </header>
  );
}
