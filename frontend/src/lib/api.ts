const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8002";

async function get(path: string) {
  const res = await fetch(API + path);
  if (!res.ok) { const b = await res.json().catch(() => ({})); throw new Error(b.detail || ("HTTP " + res.status)); }
  return res.json();
}
async function post<T>(path: string, body?: unknown): Promise<T> {
  const res = await fetch(API + path, { method: "POST", headers: { "Content-Type": "application/json" }, body: body ? JSON.stringify(body) : undefined });
  if (!res.ok) { const b = await res.json().catch(() => ({})); throw new Error(b.detail || ("HTTP " + res.status)); }
  return res.json();
}
async function put(path: string, body?: unknown) {
  const res = await fetch(API + path, { method: "PUT", headers: { "Content-Type": "application/json" }, body: body ? JSON.stringify(body) : undefined });
  if (!res.ok) { const b = await res.json().catch(() => ({})); throw new Error(b.detail || ("HTTP " + res.status)); }
  return res.json();
}

import type { SMIDetailResponse, ScannerResponse, ConfigResponse } from "@/types";
export const api = {
  smi: (ticker: string, refresh?: boolean): Promise<SMIDetailResponse> => get("/api/smi/" + ticker + "/detail" + (refresh ? "?refresh=true" : "")),
  scanner: (): Promise<ScannerResponse> => get("/api/scanner"),
  config: (): Promise<ConfigResponse> => get("/api/config"),
  updateClawbyKey: (key: string): Promise<{status:string}> => put("/api/config/clawby-key", {api_key: key}),
  updateWatchlist: (tickers: string[]): Promise<{status:string}> => put("/api/config/watchlist", {tickers}),
  testClawby: (): Promise<{success:boolean;message:string}> => get("/api/config/test-clawby"),
  llmConfig: () => get("/api/config/llm-config"),
  updateLlmConfig: (data: Record<string, unknown>) => put("/api/config/llm-config", data),
  smiBatch: (tickers: string[]) => post<Record<string,{smi:number;level:string}>>("/api/smi/batch", {tickers}),
  marketOverview: () => get<{counts:Record<string,number>;market_smi:number;total:number}>("/api/smi/market-overview"),
};
