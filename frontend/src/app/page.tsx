"use client";
import { useState, useEffect } from "react";
import Sidebar from "@/components/layout/sidebar";
import Topbar from "@/components/layout/topbar";
import SMIGauge from "@/components/dashboard/smi-gauge";
import SMIBreakdown from "@/components/dashboard/smi-breakdown";
import SMIChart from "@/components/dashboard/smi-chart";
import SignalCard from "@/components/dashboard/signal-card";
import { api } from "@/lib/api";
import { BarChart3, Loader2, Star, RefreshCw } from "lucide-react";
import type { SMIDetailResponse } from "@/types";

export default function DashboardPage() {
  const [ticker, setTicker] = useState("AAPL");
  const [data, setData] = useState<SMIDetailResponse | null>(null);
  const [marketCounts, setMarketCounts] = useState<Record<string,number>>({bearish:0,neutral:0,bullish:0});
  const [marketSmi, setMarketSmi] = useState(50);
  const [loading, setLoading] = useState(true);
  const [watchlist, setWatchlist] = useState<string[]>(["AAPL", "NVDA", "TSLA", "MSFT", "AMZN"]);
  const [favSaving, setFavSaving] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  const onWatchlistChange = async (newList: string[]) => {
    try {
      await api.updateWatchlist(newList);
      setWatchlist(newList);
    } catch (err) {
      console.error("Failed to update watchlist", err);
    }
  };

  const load = (t: string) => {
    setLoading(true);
    setTicker(t);
    api.smi(t).then(d => { setData(d); setLoading(false); }).catch(() => setLoading(false));
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      const d = await api.smi(ticker, true);
      setData(d);
    } catch (err) {
      console.error("Refresh failed", err);
    } finally {
      setRefreshing(false);
    }
  };

  useEffect(() => {
    load("AAPL");
    api.config().then(function(c) {
      if (c.watchlist?.length) setWatchlist(c.watchlist);
    }).catch(function() {});
    api.marketOverview().then(function(m) {
      setMarketCounts(m.counts);
      setMarketSmi(m.market_smi);
    }).catch(function() {});
  }, []);

  const isInWatchlist = watchlist.includes(ticker);

  const toggleWatchlist = async () => {
    setFavSaving(true);
    try {
      let newList: string[];
      if (isInWatchlist) {
        newList = watchlist.filter(t => t !== ticker);
        if (newList.length === 0) { setFavSaving(false); return; }
      } else {
        newList = [...watchlist, ticker];
      }
      await onWatchlistChange(newList);
    } catch (err) {
      console.error("Failed to update watchlist", err);
    } finally {
      setFavSaving(false);
    }
  };

  return (
    <div className="flex min-h-screen">
      <Sidebar activeTicker={ticker} onSelect={load} watchlist={watchlist} onWatchlistChange={onWatchlistChange}
        activeSmi={data?.smi} />
      <div className="flex-1 flex flex-col">
        <Topbar onSearch={load} />
        <main className="flex-1 p-5 overflow-y-auto">
          <div className="max-w-6xl mx-auto">
            {/* Market Overview Row */}
            <div className="grid grid-cols-4 gap-3 mb-5">
              <div className="card p-3 text-center">
                <div className="text-[10px] text-[#4a5568] uppercase">偏空</div>
                <div className="text-lg font-bold text-[#ef5350]">{(marketCounts.bearish||0)+(marketCounts.extreme_bearish||0)}</div>
              </div>
              <div className="card p-3 text-center">
                <div className="text-[10px] text-[#4a5568] uppercase">中性</div>
                <div className="text-lg font-bold text-[#ffa726]">{marketCounts.neutral||0}</div>
              </div>
              <div className="card p-3 text-center">
                <div className="text-[10px] text-[#4a5568] uppercase">偏多</div>
                <div className="text-lg font-bold text-[#26a69a]">{(marketCounts.bullish||0)+(marketCounts.extreme_bullish||0)}</div>
              </div>
              <div className="card p-3 text-center">
                <div className="text-[10px] text-[#4a5568] uppercase">市场 SMI</div>
                <div className="text-lg font-bold" style={{color: marketSmi >= 60 ? "#26a69a" : marketSmi >= 40 ? "#ffa726" : "#ef5350"}}>{Math.round(marketSmi)}</div>
              </div>
            </div>

            {/* Main Content */}
            {loading ? (
              <div className="flex items-center justify-center h-64"><Loader2 size={24} className="animate-spin text-[#7c8db5]" /></div>
            ) : data ? (
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
                {/* Left: Gauge + Info */}
              <div className="space-y-4">
                    <div className="card p-3">
                      <div className="flex items-center justify-between">
                        <div className="text-lg font-semibold text-[#e2e8f0]">{data.ticker}</div>
                        <div className="flex items-center gap-2">
                          <button onClick={handleRefresh} disabled={refreshing || loading}
                            title="刷新数据"
                            className={"flex items-center gap-1 text-xs px-2 py-1 rounded transition-colors " + (refreshing ? "text-[#3b82f6]" : "text-[#4a5568] hover:text-[#7c8db5] bg-[#1f2937]/50 hover:bg-[#2d3748]/50")}>
                            <RefreshCw size={12} className={refreshing ? "animate-spin" : ""} />
                            {refreshing ? "刷新中" : "刷新"}
                          </button>
                          <button onClick={toggleWatchlist} disabled={favSaving}
                        title={isInWatchlist ? "从自选移除" : "添加到自选"}
                        className={"flex items-center gap-1 text-xs px-2 py-1 rounded transition-colors " + (isInWatchlist ? "text-[#ffa726] hover:text-[#ffc107] bg-[#ffa726]/10" : "text-[#4a5568] hover:text-[#7c8db5] bg-[#1f2937]/50 hover:bg-[#2d3748]/50")}>
                        {favSaving ? <Loader2 size={12} className="animate-spin" /> : <Star size={12} className={isInWatchlist ? "fill-[#ffa726]" : ""} />}
                        {isInWatchlist ? "已自选" : "自选"}
                      </button>
                    </div></div>
                    {data.price_current > 0 && (
                      <div className="flex items-center gap-2 mt-1">
                        <span className="text-sm text-[#7c8db5]">${data.price_current.toFixed(2)}</span>
                        <span className={"text-xs " + (data.price_change_pct >= 0 ? "text-[#26a69a]" : "text-[#ef5350]")}>
                          {data.price_change_pct >= 0 ? "+" : ""}{data.price_change_pct?.toFixed(2)}%
                        </span>
                      </div>
                    )}
                  </div>
                  <SMIGauge smi={data.smi} />
                  <SignalCard signal={data.signal} detail={data.signal_detail} />
                </div>

                {/* Center: Breakdown */}
                <div>
                  <SMIBreakdown dimensions={data.dimensions || []} />
                </div>

                {/* Right: Chart */}
                <div className="lg:col-span-1">
                  <SMIChart history={data.history || []} />
                </div>
              </div>
            ) : (
              <div className="card p-12 text-center">
                <BarChart3 size={48} className="mx-auto mb-4 text-[#2d3748]" />
                <p className="text-[#7c8db5]">选择一个股票查看 SMI 数据</p>
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  );
}
