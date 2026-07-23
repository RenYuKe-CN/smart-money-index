"use client";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend } from "recharts";

export default function SMIChart({ history }) {
  if (!history || history.length < 2) {
    return <div className="card-elevated p-4 text-center text-xs text-[#4a5568] py-8">No history data</div>;
  }
  var prices = history.map(function(h) { return h.price; }).filter(function(p) { return p > 0; });
  var pMin = Math.min.apply(null, prices);
  var pMax = Math.max.apply(null, prices);
  var pRange = pMax - pMin || 1;
  var data = history.map(function(h) {
    return { date: h.date.slice(5), smi: h.smi, priceNorm: h.price > 0 ? ((h.price - pMin) / pRange) * 80 + 10 : 50 };
  });
  return (
    <div className="card-elevated p-4">
      <div className="text-xs text-[#7c8db5] mb-3">SMI History vs Price</div>
      <ResponsiveContainer width="100%" height={220}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
          <XAxis dataKey="date" tick={{fill: "#4a5568", fontSize: 10}} tickLine={false} />
          <YAxis domain={[0, 100]} tick={{fill: "#4a5568", fontSize: 10}} />
          <Tooltip contentStyle={{background: "#1a1d2e", border: "1px solid #2d3748", borderRadius: 6, fontSize: 12}} labelStyle={{color: "#e2e8f0"}} />
          <Legend wrapperStyle={{fontSize: 11, color: "#7c8db5"}} />
          <Line type="monotone" dataKey="smi" stroke="#3b82f6" strokeWidth={2} dot={false} name="SMI" />
          <Line type="monotone" dataKey="priceNorm" stroke="#ffa726" strokeWidth={1.5} dot={false} strokeDasharray="4 2" name="Price (norm)" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
