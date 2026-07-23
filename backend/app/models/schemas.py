from __future__ import annotations
from typing import Any
from pydantic import BaseModel

class ConfigResponse(BaseModel):
    clawby_configured: bool = False
    clawby_status: str = "unknown"

class SMIRequest(BaseModel):
    ticker: str

class SMIDimension(BaseModel):
    name: str
    key: str
    score: float
    weight: float
    trend: str         # up / down / flat
    detail: str = ""

class SMIResponse(BaseModel):
    ticker: str
    smi: float
    level: str         # bullish / bearish / neutral
    change_1d: float = 0
    change_1w: float = 0
    change_1m: float = 0
    dimensions: list[SMIDimension] = []
    signal: str | None = None       # bullish_divergence / bearish_divergence / none
    signal_detail: str = ""
    updated_at: str = ""

class SMIHistoryPoint(BaseModel):
    date: str
    smi: float
    price: float

class SMIDetailResponse(SMIResponse):
    history: list[SMIHistoryPoint] = []
    price_current: float = 0
    price_change_pct: float = 0

class ScannerItem(BaseModel):
    ticker: str
    price: float
    change_pct: float
    smi: float
    level: str
    signal: str | None = None

class ScannerResponse(BaseModel):
    items: list[ScannerItem] = []
    total: int = 0
    market_smi: float = 50

class SignalItem(BaseModel):
    id: str
    ticker: str
    type: str           # bullish_divergence / bearish_divergence
    smi: float
    smi_change: float
    price_change: float
    detected_at: str
    detail: str = ""
