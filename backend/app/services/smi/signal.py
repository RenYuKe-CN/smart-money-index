from __future__ import annotations
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from app.config import settings

SIGNAL_FILE = Path(settings.data_dir) / "smi_history.json"
SMI_CACHE = {}  # ticker -> [{date, smi, price}]

def load_history() -> dict:
    if SIGNAL_FILE.exists():
        return json.loads(SIGNAL_FILE.read_text())
    return {}

def save_history(data: dict) -> None:
    SIGNAL_FILE.parent.mkdir(parents=True, exist_ok=True)
    SIGNAL_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False))

async def get_smi_history(ticker: str) -> list[dict]:
    if ticker not in SMI_CACHE:
        all_h = load_history()
        SMI_CACHE.update(all_h)
    return SMI_CACHE.get(ticker, [])

async def save_smi_point(ticker: str, smi: float, price: float) -> None:
    all_h = load_history()
    hist = all_h.get(ticker, [])
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if hist and hist[-1]["date"] == today:
        hist[-1] = {"date": today, "smi": smi, "price": price}
    else:
        hist.append({"date": today, "smi": smi, "price": price})
    hist = hist[-90:]  # Keep 90 days
    all_h[ticker] = hist
    SMI_CACHE[ticker] = hist
    save_history(all_h)

async def load_smi_cache() -> dict:
    return SMI_CACHE

def detect_signals(smi: float, prices: list[float], window: int = 5) -> dict:
    """Detect divergence between SMI and price. Returns signal dict."""
    if len(prices) < window or len(prices) < window:
        return {"type": "none", "detail": "数据不足", "confidence": 0}
    
    smi_trend = _trend([smi])  # We only have current SMI for now
    price_slope = _slope(prices[-window:])
    
    # For divergence detection, compare current SMI with price trend
    # If price is declining but SMI indicates bullish → bullish divergence
    # If price is rising but SMI indicates bearish → bearish divergence
    
    if price_slope < -0.5 and smi > 60:
        conf = min(abs(price_slope) * 20, 100)
        return {"type": "bullish_divergence", "detail": f"价格下跌但 SMI {round(smi)} 偏多，机构可能在吸筹", "confidence": round(conf)}
    elif price_slope > 0.5 and smi < 40:
        conf = min(price_slope * 20, 100)
        return {"type": "bearish_divergence", "detail": f"价格上涨但 SMI {round(smi)} 偏空，机构可能在出货", "confidence": round(conf)}
    return {"type": "none", "detail": "SMI 与价格趋势一致", "confidence": 0}

def _trend(values: list[float]) -> float:
    if len(values) < 2: return 0
    return _slope(values)

def _slope(values: list[float]) -> float:
    n = len(values)
    if n < 2: return 0
    xs = list(range(n))
    mx = sum(xs) / n
    my = sum(values) / n
    num = sum((xs[i] - mx) * (values[i] - my) for i in range(n))
    den = sum((xs[i] - mx) ** 2 for i in range(n))
    return num / den if den != 0 else 0
