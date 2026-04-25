import { Link } from "react-router-dom";
import { Star, Moon, Heart, Shield, Lock } from "@phosphor-icons/react";

export default function Landing() {
  return (
    <div className="relative min-h-[calc(100vh-4rem)] overflow-hidden">
      <div className="absolute inset-0 starfield opacity-70 pointer-events-none" />
      <div className="absolute inset-0 pointer-events-none opacity-30"
        style={{ backgroundImage: "url('https://images.pexels.com/photos/34634037/pexels-photo-34634037.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940')", backgroundSize: 'cover', backgroundPosition: 'center' }}/>
      <div className="absolute inset-0 bg-gradient-to-b from-[#0A0305]/40 via-[#0A0305]/70 to-[#0A0305]" />

      <section className="relative z-10 max-w-7xl mx-auto px-6 md:px-10 pt-24 pb-32">
        <div className="grid md:grid-cols-12 gap-10 items-center">
          <div className="md:col-span-7">
            <p className="text-xs tracking-[0.3em] uppercase text-[#D4AF37] mb-6 flex items-center gap-2">
              <Lock size={12} weight="fill" /> Private · Invitation only
            </p>
            <h1 className="font-serif text-5xl sm:text-6xl lg:text-7xl text-[#F3E6C6] leading-[1.05] tracking-tight mb-6">
              When two charts<br/><span className="italic text-[#D4AF37]">align</span>, the universe listens.
            </h1>
            <p className="text-lg text-[#C2A3A8] leading-relaxed max-w-xl mb-10">
              Stars Connection is an ultra-private referral-only matchmaking circle, reading each member's janam kundali through the Swiss Ephemeris to surface only the most resonant connections.
            </p>
            <div className="flex flex-wrap gap-4">
              <Link to="/login" data-testid="hero-cta-login" className="px-8 py-4 bg-[#D4AF37] text-[#0A0305] font-medium uppercase tracking-wider text-sm hover:bg-[#B88A2A] transition shadow-[0_0_32px_rgba(212,175,55,0.25)]">
                Member login
              </Link>
              <span className="px-8 py-4 border border-[#D4AF37]/30 text-[#C2A3A8] uppercase tracking-wider text-xs flex items-center">
                Have an invite? Use the link sent to you
              </span>
            </div>
            <div className="mt-10 flex items-center gap-6 text-xs text-[#8A6B72] tracking-widest uppercase">
              <span>⋆ Swiss Ephemeris</span>
              <span>⋆ Ashtakoota 8 Gunas</span>
              <span>⋆ Mangal Dosha</span>
              <span>⋆ Consent-based contact</span>
            </div>
          </div>
          <div className="md:col-span-5 hidden md:block">
            <div className="relative aspect-square">
              <div className="absolute inset-0 rounded-full border border-[#D4AF37]/25 animate-slow-spin" />
              <div className="absolute inset-8 rounded-full border border-[#D4AF37]/20 animate-reverse-spin" />
              <div className="absolute inset-16 rounded-full border border-[#D4AF37]/15 animate-slow-spin" />
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="w-48 h-48 rounded-full bg-gradient-to-br from-[#7A1E2C] to-[#2A0E18] flex items-center justify-center shadow-[0_0_80px_rgba(212,175,55,0.15)]">
                  <Moon size={90} weight="duotone" className="text-[#D4AF37]" />
                </div>
              </div>
              {["Ashwini","Rohini","Magha","Hasta","Anuradha","Shravana","Revati","Pushya"].map((n, i) => (
                <div key={n} className="absolute text-[10px] tracking-[0.3em] uppercase text-[#D4AF37]/70"
                     style={{ top: `${50 + 47 * Math.sin((i / 8) * 2 * Math.PI)}%`, left: `${50 + 47 * Math.cos((i / 8) * 2 * Math.PI)}%`, transform: 'translate(-50%,-50%)' }}>
                  {n}
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section className="relative z-10 max-w-7xl mx-auto px-6 md:px-10 pb-32">
        <div className="grid md:grid-cols-3 gap-10">
          {[
            { i: Star, t: "Real ephemeris, not guesswork", d: "Moon sign, Nakshatra & Rashi computed via Swiss Ephemeris with sidereal Lahiri ayanamsa." },
            { i: Heart, t: "Ashtakoota 8-guna score", d: "Full breakdown across Varna, Vashya, Tara, Yoni, Graha Maitri, Gana, Bhakoot & Nadi — out of 36." },
            { i: Shield, t: "Consent-based contact", d: "Phone numbers are never auto-shared. Each connection is gated by a request the other person can accept or decline." },
          ].map(({ i: Icon, t, d }) => (
            <div key={t} className="p-8 bg-[#1A0810]/60 border border-[#D4AF37]/10 backdrop-blur-sm">
              <Icon size={32} weight="duotone" className="text-[#D4AF37] mb-5" />
              <h3 className="font-serif text-2xl text-[#F3E6C6] mb-3">{t}</h3>
              <p className="text-sm text-[#C2A3A8] leading-relaxed">{d}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
