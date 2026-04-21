import { Link, useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { Star, SignOut } from "@phosphor-icons/react";

export default function Navbar() {
  const { user, logout } = useAuth();
  const nav = useNavigate();
  const loc = useLocation();
  const handleLogout = async () => { await logout(); nav("/"); };

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
              {user.profile_complete && (
                <Link to="/dashboard" className={`hover:text-[#D4AF37] transition ${loc.pathname === '/dashboard' ? 'text-[#D4AF37]' : ''}`} data-testid="nav-dashboard">
                  Dashboard
                </Link>
              )}
              <span className="hidden sm:inline text-[#8A6B72]">{user.name}</span>
              <button onClick={handleLogout} data-testid="nav-logout" className="flex items-center gap-1.5 px-3 py-1.5 border border-[#D4AF37]/30 rounded-sm hover:border-[#D4AF37] hover:text-[#D4AF37] transition">
                <SignOut size={16} /> Logout
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="hover:text-[#D4AF37] transition" data-testid="nav-login">Log in</Link>
              <Link to="/register" className="px-4 py-1.5 bg-[#D4AF37] text-[#0A0305] font-medium hover:bg-[#B88A2A] transition" data-testid="nav-signup">Begin</Link>
            </>
          )}
        </nav>
      </div>
    </header>
  );
}
