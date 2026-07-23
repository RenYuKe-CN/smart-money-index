"use client";
import { useEffect, useState } from "react";
import { X, Plus, Edit2, Check, Loader2 } from "lucide-react";
import { api } from "@/lib/api";

export default function Sidebar({ activeTicker, onSelect, watchlist, onWatchlistChange, activeSmi }: { activeTicker: string; onSelect: (t: string) => void; watchlist: string[]; onWatchlistChange: (w: string[]) => void; activeSmi?: number }) {
  const [smiData, setSmiData] = useState<Record<string, number>>({});
  const [editing, setEditing] = useState(false);
  const [newTicker, setNewTicker] = useState("");
  const [saving, setSaving] = useState(false);
  // Sync detail page's SMI value into sidebar so they stay consistent
  useEffect(() => {
    if (activeSmi != null && activeTicker) {
      setSmiData(prev => ({ ...prev, [activeTicker]: activeSmi }));
    }
  }, [activeTicker, activeSmi]);

  useEffect(() => {
    if (watchlist.length === 0) return;
    api.smiBatch(watchlist).then(function(r) {
      var newData: Record<string, number> = {};
      for (var t in r) { newData[t] = r[t].smi; }
      setSmiData(newData);
    }).catch(function() {});
  }, [watchlist]);

  const smiColor = (s: number) => s >= 60 ? "text-[#26a69a]" : s >= 40 ? "text-[#ffa726]" : "text-[#ef5350]";

  const removeTicker = async (ticker: string) => {
    setSaving(true);
    await onWatchlistChange(watchlist.filter(t => t !== ticker));
    setSaving(false);
  };

  const addTicker = async () => {
    const t = newTicker.trim().toUpperCase();
    if (!t || watchlist.includes(t)) return;
    setSaving(true);
    await onWatchlistChange([...watchlist, t]);
    setNewTicker("");
    setSaving(false);
  };

  return (
    <aside className="w-56 min-h-screen bg-[#0a0e17] border-r border-[#1f2937] flex flex-col">
      <div className="px-4 py-4 border-b border-[#1f2937]">
        <div className="text-sm font-semibold text-[#e2e8f0]">Smart Money Index</div>
        <div className="text-[10px] text-[#7c8db5]">Institutional Sentiment</div>
      </div>
      <div className="px-3 py-3 flex items-center justify-between">
        <span className="text-[10px] text-[#4a5568] uppercase tracking-wider">Watchlist</span>
        <button onClick={() => setEditing(!editing)} className="text-[#4a5568] hover:text-[#7c8db5] transition-colors" title={editing ? "完成" : "编辑"}>
          {editing ? <Check size={14} /> : <Edit2 size={14} />}
        </button>
      </div>
      <nav className="flex-1 px-2 space-y-0.5 overflow-y-auto">
        {watchlist.map(t => (
          <button key={t} onClick={() => onSelect(t)}
            className={"w-full flex items-center justify-between px-3 py-2 rounded text-sm transition-colors " + (activeTicker === t ? "bg-[#1a73e8]/10 text-[#3b82f6]" : "text-[#7c8db5] hover:text-[#e2e8f0] hover:bg-[#111827]")}>
            <span className="font-medium flex items-center gap-1.5">
              {editing && (
                <span onClick={(e) => { e.stopPropagation(); removeTicker(t); }}
                  className="text-[#ef5350] hover:text-[#ff6659] cursor-pointer">
                  <X size={12} />
                </span>
              )}
              {t}
            </span>
            <span className={"font-mono text-xs " + smiColor(smiData[t] || 50)}>
              {smiData[t] != null ? Math.round(smiData[t]) : "--"}
            </span>
          </button>
        ))}
        {editing && (
          <div className="flex items-center gap-1 px-2 py-1">
            <input value={newTicker} onChange={e => setNewTicker(e.target.value.toUpperCase())}
              onKeyDown={e => { if (e.key === 'Enter') addTicker(); }}
              placeholder="添加代码..."
              className="flex-1 bg-[#111827] border border-[#2d3748] rounded px-2 py-1.5 text-xs text-[#e2e8f0] placeholder-[#4a5568] focus:outline-none focus:border-[#3b82f6]" />
            <button onClick={addTicker} disabled={!newTicker.trim() || saving}
              className="text-[#3b82f6] hover:text-[#5a9cf6] disabled:text-[#4a5568] transition-colors">
              {saving ? <Loader2 size={14} className="animate-spin" /> : <Plus size={14} />}
            </button>
          </div>
        )}
      </nav>
      <div className="px-4 py-3 border-t border-[#1f2937] text-[10px] text-[#4a5568]">v0.1 · Clawby</div>
    </aside>
  );
}
