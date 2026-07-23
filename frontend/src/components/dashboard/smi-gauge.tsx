"use client";
export default function SMIGauge({ smi }: { smi: number }) {
  var pct = Math.max(0, Math.min(100, smi));
  var color = pct >= 80 ? "#00c853" : pct >= 60 ? "#26a69a" : pct >= 40 ? "#ffa726" : pct >= 20 ? "#ef5350" : "#d50000";
  var level = pct >= 80 ? "Extreme Bullish" : pct >= 60 ? "Bullish" : pct >= 40 ? "Neutral" : pct >= 20 ? "Bearish" : "Extreme Bearish";
  return (
    <div className="card-elevated p-5">
      <div className="flex items-center justify-between mb-1">
        <span className="text-xs text-[#7c8db5]">Smart Money Index</span>
        <span className="text-xs text-[#7c8db5]">SMI</span>
      </div>
      <div className="flex items-end gap-3 mb-2">
        <span className="smi-score" style={{color: color}}>{Math.round(pct)}</span>
        <span className="text-sm mb-1" style={{color: color}}>{level}</span>
      </div>
      <div className="w-full h-2.5 bg-[#1f2937] rounded-full overflow-hidden">
        <div className="h-full rounded-full transition-all duration-500" style={{width: pct + "%", backgroundColor: color}} />
      </div>
      <div className="flex justify-between text-[10px] text-[#4a5568] mt-1">
        <span>Bearish 0</span>
        <span>50</span>
        <span>Bullish 100</span>
      </div>
    </div>
  );
}
