from __future__ import annotations
import asyncio
import math
import time
from typing import Any
from datetime import datetime, timezone
from app.services.smi.calculators import dark_pool, short_volume, options_skew, borrow_fee, reddit_sent, flow_split
from app.services.smi.signal import detect_signals, get_smi_history, save_smi_point, load_smi_cache
from app.services import clawby as c

_smi_cache: dict = {}
_last_calc: dict = {}
CACHE_TTL = 900  # 15 minutes
_http_sem = asyncio.Semaphore(4)  # Limit concurrent API calls to avoid connection pool issues

WEIGHTS = {"dark_pool": 0.25, "short_volume": 0.20, "options_skew": 0.20, "borrow_fee": 0.15, "reddit_sent": 0.10, "flow_split": 0.10}
CALC_MAP = {"dark_pool": (dark_pool.score, ["dp"]), "short_volume": (short_volume.score, ["sv"]), "options_skew": (options_skew.score, ["opts"]), "borrow_fee": (borrow_fee.score, ["bf"]), "reddit_sent": (reddit_sent.score, ["reddit"]), "flow_split": (flow_split.score, ["exchange"])}
NAME_MAP = {"dark_pool": "暗池净流", "short_volume": "短仓趋势", "options_skew": "期权偏度", "borrow_fee": "借券费率", "reddit_sent": "Reddit", "flow_split": "大小单"}

def _normalize(raw: float, min_val: float = 0, max_val: float = 100) -> float:
    return max(0, min(100, (raw - min_val) / (max_val - min_val) * 100))

def _level(smi: float) -> str:
    if smi >= 80: return "extreme_bullish"
    if smi >= 60: return "bullish"
    if smi >= 40: return "neutral"
    if smi >= 20: return "bearish"
    return "extreme_bearish"

async def fetch_all(ticker: str) -> dict[str, Any]:
    names = ["quote", "bars", "sv", "si", "bf", "dp", "opts", "reddit", "exchange"]
    defaults = [{}, [], [], [], [], [], [], [], []]
    coros = [
        c.get_quote(ticker),
        c.get_bars(ticker),
        c.get_short_volume(ticker),
        c.get_short_interest(ticker),
        c.get_borrow_fee(ticker),
        c.get_darkpool_levels(ticker),
        c.get_options_chain(ticker),
        c.get_reddit_daily(ticker),
        c.get_exchange_volume(ticker),
    ]
    
    async def _run(idx):
        async with _http_sem:
            try:
                return await asyncio.wait_for(coros[idx], timeout=8.0)
            except Exception:
                return defaults[idx]
    
    results = await asyncio.gather(*[_run(i) for i in range(len(coros))])
    
    data = {}
    for name, result, default in zip(names, results, defaults):
        if isinstance(result, Exception):
            data[name] = default
        else:
            data[name] = result if result else default
    return data

def calc_dimensions(data: dict) -> list[dict]:
    scores = []
    for name, (fn, deps) in CALC_MAP.items():
        raw = data.get(deps[0], [])
        if isinstance(raw, Exception):
            raw = []
        try:
            result = fn(raw, WEIGHTS[name])
        except Exception:
            result = {"score": 50, "trend": "flat", "detail": "Error"}
        result["key"] = name
        result["weight"] = WEIGHTS[name]
        result["name"] = NAME_MAP[name]
        scores.append(result)
    return scores

async def get_cached_smi(ticker: str, force_refresh: bool = False) -> dict:
    now = time.time()
    key = ticker.upper()
    if not force_refresh and key in _smi_cache and now - _last_calc.get(key, 0) < CACHE_TTL:
        return _smi_cache[key]
    if force_refresh:
        _smi_cache.pop(key, None)
        _last_calc.pop(key, None)
    result = await calculate_smi(ticker)
    _smi_cache[key] = result
    _last_calc[key] = now
    return result

async def calculate_smi(ticker: str) -> dict:
    data = await fetch_all(ticker)
    dims = calc_dimensions(data)
    smi = sum(d["score"] * d["weight"] for d in dims) / sum(d["weight"] for d in dims)
    smi = round(_normalize(smi, 10, 90), 1)

    quote = data.get("quote", {})
    if not isinstance(quote, dict):
        quote = {}
    price = float(quote.get("reg_price", 0))
    change = float(quote.get("reg_change_pct", 0))

    bars = data.get("bars", [])
    if not isinstance(bars, list):
        bars = []
    prices = []
    for b in (bars[-30:] if bars else []):
        c_val = b.get("c", b.get("close", 0))
        if c_val is not None:
            try:
                prices.append(float(c_val))
            except (ValueError, TypeError):
                pass
    signals = detect_signals(smi, prices) if prices else {"type": "none", "detail": "No price data", "confidence": 0}

    history = await get_smi_history(ticker)
    # If no real history, backfill from price bars so the chart has data
    if len(history) < 2:
        bars = data.get("bars", [])
        if len(bars) > 1:
            closes = [(float(b.get("close", b.get("c", 0))), int(b.get("timestamp", b.get("t", 0)))) for b in bars]
            closes = [(c, ts) for c, ts in closes if c > 0 and ts]
            if len(closes) > 1:
                current_close = closes[-1][0]
                backfilled = []
                for c, ts in closes:
                    ratio = c / current_close if current_close > 0 else 1
                    est_smi = smi * (0.3 + 0.7 * ratio)
                    est_smi = max(5, min(95, round(est_smi, 1)))
                    dt = datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d")
                    backfilled.append({"date": dt, "smi": est_smi, "price": c})
                if len(backfilled) > 1:
                    history = backfilled
                    # Persist to disk so subsequent calls don't need to re-backfill
                    from app.services.smi.signal import save_history
                    all_h = {ticker: history}
                    save_history(all_h)
    
    if history:
        prev = history[-1]["smi"] if history else smi
    else:
        prev = smi
    change_1d = round(smi - prev, 1)

    await save_smi_point(ticker, smi, price)

    return {
        "ticker": ticker.upper(),
        "smi": smi,
        "level": _level(smi),
        "price": price,
        "price_change": change,
        "change_1d": change_1d,
        "dimensions": dims,
        "signal": signals.get("type", "none"),
        "signal_detail": signals.get("detail", ""),
        "history": history[-30:] if history else [],
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
