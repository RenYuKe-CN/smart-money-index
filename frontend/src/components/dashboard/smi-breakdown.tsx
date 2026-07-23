"use client";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";

export default function SMIBreakdown({ dimensions }) {
  if (!dimensions || dimensions.length === 0) {
    return <div className="card-elevated p-4 text-xs text-[#4a5568] text-center py-6">No data</div>;
  }
  return (
    <div className="card-elevated p-4">
      <div className="text-xs text-[#7c8db5] mb-3">Six Dimensions</div>
      <div className="space-y-2.5">
        {dimensions.map(function(d) {
          var scoreColor = d.score >= 60 ? "#26a69a" : d.score >= 40 ? "#ffa726" : "#ef5350";
          var TrendIcon = d.trend === "up" ? TrendingUp : d.trend === "down" ? TrendingDown : Minus;
          return (
            <div key={d.key}>
              <div className="flex items-center justify-between text-xs mb-1">
                <span className="text-[#e2e8f0] font-medium">{d.name}</span>
                <div className="flex items-center gap-2">
                  <span className="font-mono" style={{color: scoreColor}}>{Math.round(d.score)}</span>
                  <TrendIcon size={12} className={d.trend === "up" ? "text-[#26a69a]" : d.trend === "down" ? "text-[#ef5350]" : "text-[#4a5568]"} />
                </div>
              </div>
              <div className="w-full h-1.5 bg-[#1f2937] rounded-full overflow-hidden">
                <div className="h-full rounded-full" style={{width: d.score + "%", backgroundColor: scoreColor}} />
              </div>
              <div className="text-[10px] text-[#4a5568] mt-0.5">{d.detail}</div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
