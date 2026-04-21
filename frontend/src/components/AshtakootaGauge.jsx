export default function AshtakootaGauge({ score, max = 36, size = 96 }) {
  const pct = Math.min(1, Math.max(0, score / max));
  const r = size / 2 - 6;
  const c = 2 * Math.PI * r;
  const off = c * (1 - pct);
  const color = score >= 28 ? "#D4AF37" : score >= 18 ? "#CFAE3D" : "#8A6B72";
  return (
    <div className="relative inline-flex items-center justify-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="rotate-[-90deg]">
        <circle cx={size / 2} cy={size / 2} r={r} stroke="#2A0E18" strokeWidth="4" fill="none" />
        <circle
          cx={size / 2} cy={size / 2} r={r}
          stroke={color} strokeWidth="4" fill="none"
          strokeDasharray={c} strokeDashoffset={off}
          strokeLinecap="round"
          style={{ transition: "stroke-dashoffset 1s ease" }}
        />
      </svg>
      <div className="absolute flex flex-col items-center">
        <span className="font-serif text-2xl text-[#F3E6C6] leading-none">{score}</span>
        <span className="text-[10px] tracking-[0.2em] uppercase text-[#8A6B72] mt-0.5">/ {max}</span>
      </div>
    </div>
  );
}
