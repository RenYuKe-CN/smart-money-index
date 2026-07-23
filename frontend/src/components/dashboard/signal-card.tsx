"use client";
import { TrendingUp, TrendingDown, Info } from "lucide-react";

export default function SignalCard({ signal, detail }) {
  if (!signal || signal === "none") {
    return (
      <div className="card-elevated p-4 flex items-center gap-3">
        <Info size={16} className="text-[#4a5568]" />
        <div>
          <div className="text-xs text-[#4a5568]">No signal</div>
          <div className="text-[10px] text-[#4a5568] mt-0.5">SMI aligned with price</div>
        </div>
      </div>
    );
  }
  var isBullish = signal === "bullish_divergence";
  var Icon = isBullish ? TrendingUp : TrendingDown;
  return (
    <div className={"card-elevated p-4 border-l-4 " + (isBullish ? "border-[#26a69a]" : "border-[#ef5350]")}>
      <div className="flex items-center gap-2">
        <Icon size={18} className={isBullish ? "text-[#26a69a]" : "text-[#ef5350]"} />
        <span className={"text-sm font-semibold " + (isBullish ? "text-[#26a69a]" : "text-[#ef5350]")}>
          {isBullish ? "Bullish Divergence" : "Bearish Divergence"}
        </span>
      </div>
      <p className="text-xs text-[#7c8db5] mt-1">{detail || ""}</p>
    </div>
  );
}
