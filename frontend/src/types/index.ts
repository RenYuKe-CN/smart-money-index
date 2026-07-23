export interface SMIDimension { name: string; key: string; score: number; weight: number; trend: string; detail: string; }
export interface SMIResponse { ticker: string; smi: number; level: string; change_1d: number; dimensions: SMIDimension[]; signal?: string | null; signal_detail?: string; }
export interface SMIHistoryPoint { date: string; smi: number; price: number; }
export interface SMIDetailResponse extends SMIResponse { history: SMIHistoryPoint[]; price_current: number; price_change_pct: number; }
export interface ScannerItem { ticker: string; price: number; change_pct: number; smi: number; level: string; signal?: string | null; }
export interface ScannerResponse { items: ScannerItem[]; total: number; market_smi: number; }
export interface ConfigResponse { clawby_configured: boolean; clawby_status: string; watchlist: string[]; api_key_preview: string; }
