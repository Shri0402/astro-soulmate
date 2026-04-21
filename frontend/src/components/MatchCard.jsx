import { Link } from "react-router-dom";
import AshtakootaGauge from "./AshtakootaGauge";
import { MapPin, Lock } from "@phosphor-icons/react";

function computeAge(dob) {
  if (!dob) return null;
  const d = new Date(dob);
  return Math.floor((Date.now() - d.getTime()) / (365.25 * 24 * 3600 * 1000));
}

export default function MatchCard({ match, locked = false }) {
  const age = computeAge(match.match_dob);
  const CardInner = (
    <div className={`group relative h-full border border-[#D4AF37]/15 bg-[#2A0E18] p-6 transition-all duration-300 hover:border-[#D4AF37]/60 hover:-translate-y-1 hover:shadow-[0_12px_40px_rgba(212,175,55,0.08)] ${locked ? 'overflow-hidden' : ''}`} data-testid={locked ? "match-card-locked" : "match-card"}>
      <div className={locked ? "blur-content" : ""}>
        <div className="flex items-start justify-between gap-4 mb-5">
          <div className="min-w-0 flex-1">
            <div className="text-[10px] tracking-[0.2em] uppercase text-[#8A6B72] mb-2">
              {match.score >= 28 ? "Exceptional" : match.score >= 24 ? "Excellent" : match.score >= 18 ? "Good" : "Moderate"}
            </div>
            <h3 className="font-serif text-2xl text-[#F3E6C6] leading-tight truncate">{match.match_name}</h3>
            {age && match.match_city && (
              <p className="text-sm text-[#C2A3A8] mt-1 flex items-center gap-1">
                {age} · <MapPin size={12} /> {match.match_city}
              </p>
            )}
          </div>
          <AshtakootaGauge score={match.score} max={match.max_score || 36} size={80} />
        </div>
        {match.match_bio && (
          <p className="text-sm text-[#C2A3A8] leading-relaxed line-clamp-3 mb-5">{match.match_bio}</p>
        )}
        <div className="flex items-center justify-between pt-4 border-t border-[#D4AF37]/10">
          <span className="text-xs text-[#8A6B72] uppercase tracking-[0.2em]">
            {match.score >= 18 ? "Premium match" : "Casual match"}
          </span>
          {!locked && (
            <span className="text-[#D4AF37] text-sm font-medium group-hover:underline">View Kundali →</span>
          )}
        </div>
      </div>
    </div>
  );

  if (locked) return CardInner;
  return <Link to={`/kundali/${match.match_user_id}`} className="block h-full" data-testid={`match-view-${match.match_user_id}`}>{CardInner}</Link>;
}
