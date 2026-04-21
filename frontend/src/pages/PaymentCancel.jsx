import { Link } from "react-router-dom";
import { XCircle } from "@phosphor-icons/react";

export default function PaymentCancel() {
  return (
    <div className="min-h-[calc(100vh-4rem)] starfield flex items-center justify-center px-6">
      <div className="max-w-md text-center p-10 bg-[#1A0810]/90 border border-[#D4AF37]/25">
        <XCircle size={64} weight="duotone" className="text-[#8A6B72] mx-auto mb-5" />
        <p className="text-xs tracking-[0.3em] uppercase text-[#8A6B72] mb-3">Cancelled</p>
        <h1 className="font-serif text-3xl text-[#F3E6C6] mb-4">No payment made</h1>
        <p className="text-[#C2A3A8] mb-8">Your card was not charged. You can retry any time from your dashboard.</p>
        <Link to="/dashboard" className="inline-block px-8 py-3 bg-[#D4AF37] text-[#0A0305] uppercase tracking-[0.2em] text-xs hover:bg-[#B88A2A]">
          Back to dashboard
        </Link>
      </div>
    </div>
  );
}
