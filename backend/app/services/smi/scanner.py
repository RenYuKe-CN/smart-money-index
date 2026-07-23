from __future__ import annotations
import hashlib
import random
import asyncio
from app.services.smi.engine import calculate_smi
from app.services import clawby as c

SCREENED_TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META", "SPY", "QQQ", "AMD", "INTC", "PLTR", "NFLX", "DIS", "BA", "JPM", "V", "MA", "WMT", "JNJ"]

_base_prices = {"AAPL": 320, "MSFT": 380, "GOOGL": 175, "AMZN": 230, "NVDA": 210, "TSLA": 320, "META": 530, "SPY": 740, "QQQ": 500, "AMD": 180, "INTC": 35, "PLTR": 75, "NFLX": 720, "DIS": 90, "BA": 180, "JPM": 220, "V": 280, "MA": 480, "WMT": 75, "JNJ": 160}

def _demo_score(ticker: str, dim: str) -> float:
    seed = int(hashlib.md5((ticker + dim).encode()).hexdigest()[:8], 16)
    rng = random.Random(seed)
    return max(0, min(100, 50 + rng.uniform(-35, 35)))

def _quick_smi(ticker: str) -> dict:
    dp = _demo_score(ticker, "dp")
    sv = _demo_score(ticker, "sv")
    os = _demo_score(ticker, "os")
    bf = _demo_score(ticker, "bf")
    rs = _demo_score(ticker, "rs")
    fs = _demo_score(ticker, "fs")
    smi = dp*0.25 + sv*0.20 + os*0.20 + bf*0.15 + rs*0.10 + fs*0.10
    smi = max(0, min(100, (smi - 10) / 80 * 100))
    level = "extreme_bullish" if smi >= 80 else "bullish" if smi >= 60 else "neutral" if smi >= 40 else "bearish" if smi >= 20 else "extreme_bearish"
    return {"smi": round(smi, 1), "level": level}

async def scan_market() -> list[dict]:
    results = []
    for ticker in SCREENED_TICKERS:
        demo = _quick_smi(ticker)
        price = _base_prices.get(ticker, 100)
        results.append({
            "ticker": ticker,
            "price": price,
            "change_pct": round(random.uniform(-3, 3), 2),
            "smi": demo["smi"],
            "level": demo["level"],
            "signal": None,
        })
    results.sort(key=lambda x: x["smi"], reverse=True)
    avg_smi = sum(r["smi"] for r in results) / len(results) if results else 50
    return {"items": results, "total": len(results), "market_smi": round(avg_smi, 1)}
