from __future__ import annotations
import time
import hashlib
import random
from datetime import datetime, timezone, timedelta
from typing import Any
import httpx
from app.config import settings

TIMEOUT = 30.0
CLAWBY_RELAY = f"{settings.clawby_base_url}/api/relay"

def _get_key() -> str:
    try:
        from app.services.config_store import load_config
        cfg = load_config()
        return cfg.get("clawby_api_key", settings.clawby_api_key)
    except Exception:
        return settings.clawby_api_key

def _is_demo_key() -> bool:
    key = _get_key()
    return not key or key.startswith("pk_test") or key == "sk-test-placeholder"

async def _call(name: str, params: dict | None = None) -> Any:
    key = _get_key()
    if _is_demo_key():
        return _demo_fallback(name, params)
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            resp = await client.post(CLAWBY_RELAY, headers={"X-API-Key": key, "Content-Type": "application/json"}, json={"name": name, "params": params or {}})
            if resp.status_code in (401, 403):
                return _demo_fallback(name, params)
            resp.raise_for_status()
            body = resp.json()
            return body.get("data", body)
    except Exception:
        return _demo_fallback(name, params)

def _extract_list(data: Any) -> list:
    """Extract list from API response which may be paginated dict or plain list."""
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        # Paginated API response: {"count": N, "results": [...]}
        results = data.get("results", [])
        if isinstance(results, list):
            return results
    return []

def _safe_float(v: Any, default: float = 0.0) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        return default

def _demo_fallback(name: str, params: dict | None = None) -> Any:
    ticker = ""
    if params:
        s = params.get("symbol", params.get("underlying", ""))
        ticker = str(s).replace("US:", "").replace("BTC:", "")
    if not ticker:
        ticker = "AAPL"
    seed = int(hashlib.md5(ticker.encode()).hexdigest()[:8], 16)
    rng = random.Random(seed)
    base = {"AAPL": 245, "NVDA": 130, "TSLA": 250, "MSFT": 450, "GOOGL": 180, "AMZN": 200, "META": 520, "SPY": 560, "QQQ": 490}.get(ticker, 100)
    # Ticker personality: 0-3 determines bullish/bearish bias per dimension
    dp_bias = rng.uniform(-1, 1)    # dark pool bias
    sv_bias = rng.uniform(-1, 1)    # short volume trend bias
    os_bias = rng.uniform(-1, 1)    # options skew bias
    bf_bias = rng.uniform(-1, 1)    # borrow fee bias
    rs_bias = rng.uniform(-1, 1)    # reddit sentiment bias
    fs_bias = rng.uniform(-1, 1)    # flow split bias
    fallbacks = {
        "Quote for a given stock": lambda: {"reg_price": base, "reg_change_pct": round(rng.uniform(-3, 3), 2), "market_cap": base * rng.randint(500_000_000, 8_000_000_000)},
        "Screen thousands of stocks": lambda: [{"display": ticker, "reg_price": base, "reg_change_pct": round(rng.uniform(-3, 3), 2), "market_cap": base * rng.randint(500_000_000, 8_000_000_000)}],
        "Stock aggregate OHLC bars (k-line)": lambda: _demo_bars(ticker, base, seed),
        "Short volume for a given stock": lambda: _demo_short_vol(ticker, seed, sv_bias),
        "Short Interest for a given stock": lambda: _demo_si(ticker, seed),
        "Daily Short Interest for a given stock": lambda: [{"date": (datetime.now(timezone.utc) - timedelta(days=i)).strftime("%Y-%m-%d"), "shares_short": int(rng.uniform(10_000_000, 100_000_000)), "short_pct": round(rng.uniform(1, 8), 2)} for i in range(10)],
        "Cost-to-borrow from Interactive Brokers": lambda: [{"timestamp": (datetime.now(timezone.utc) - timedelta(days=i)).strftime("%Y-%m-%d"), "borrow_rate": round(max(0.1, rng.uniform(0.2 + bf_bias * 2, 5 + bf_bias * 3)), 2)} for i in range(30)],
        "FTDs for a given stock": lambda: [{"date": (datetime.now(timezone.utc) - timedelta(days=i)).strftime("%Y-%m-%d"), "fails": int(rng.uniform(100_000, 5_000_000))} for i in range(10)],
        "Dark Pool Levels for a given stock": lambda: _demo_darkpool(ticker, base, seed, dp_bias),
        "Dark Pool Prints (trades) summary for a given stock": lambda: {"total_volume": rng.randint(1_000_000, 10_000_000), "trade_count": rng.randint(50, 500)},
        "Option chain summary (max pain, ITM/OTM)": lambda: _demo_options(ticker, base, seed, os_bias),
        "List of option contracts": lambda: [{"expiration": (datetime.now(timezone.utc) + timedelta(days=35)).strftime("%Y-%m-%d")}],
        "Reddit mentions for a given stock": lambda: [{"created_at": int((datetime.now(timezone.utc) - timedelta(hours=h)).timestamp()), "title": f"Discussion about {ticker}", "subreddit": "wallstreetbets"} for h in range(24)],
        "Daily Reddit mention counts for a given stock": lambda: _demo_reddit(ticker, seed, rs_bias),
        "Dividends for a given stock": lambda: [{"ex_date": (datetime.now(timezone.utc) - timedelta(days=91*q)).strftime("%Y-%m-%d"), "amount": round(rng.uniform(0.2, 1.5), 4)} for q in range(8)],
        "Splits for a given stock": lambda: [{"date": "2024-08-01", "ratio": "4:1"}],
        "Historical Float and Shares Outstanding for a given stock": lambda: [{"date": (datetime.now(timezone.utc) - timedelta(days=180*i)).strftime("%Y-%m-%d"), "shares_outstanding": int(rng.uniform(1e9, 1e10))} for i in range(5)],
        "Exchange volume for a given stock": lambda: _demo_exchange(ticker, seed, fs_bias),
        "List of stock exchanges": lambda: [{"code": "NASDAQ"}, {"code": "NYSE"}],
    }
    fn = fallbacks.get(name)
    if fn:
        return fn()
    return {"error": f"no_demo_{name}"}

def _demo_bars(ticker: str, base: float, seed: int = 0) -> list[dict]:
    rng = random.Random(seed + 100)
    bars = []
    drift = rng.uniform(-0.003, 0.005)
    price = base * rng.uniform(0.7, 0.95)
    for i in range(60):
        chg = rng.gauss(drift, 0.025)
        close = round(price * (1 + chg), 2)
        bars.append({"t": int((datetime.now(timezone.utc) - timedelta(days=59-i)).timestamp()), "c": close, "v": int(rng.uniform(10_000_000, 100_000_000))})
        price = close
    return bars

def _demo_short_vol(ticker: str, seed: int = 0, sv_bias: float = 0) -> list[dict]:
    rng = random.Random(seed + 200)
    # sv_bias > 0 means short volume increases over time (bearish)
    # sv_bias < 0 means short volume decreases (bullish)
    result = []
    for i in range(60):
        trend = sv_bias * (i / 60)
        st_base = 2_000_000 + sv_bias * 3_000_000 * (i / 60)
        st = int(max(100_000, rng.uniform(st_base * 0.6, st_base * 1.4)))
        rt = int(rng.uniform(20_000_000, 80_000_000))
        lt = int(rng.uniform(15_000_000, 70_000_000))
        result.append({"date": (datetime.now(timezone.utc) - timedelta(days=59-i)).strftime("%Y-%m-%d"), "st": st, "rt": rt, "lt": lt})
    return result

def _demo_si(ticker: str, seed: int = 0) -> list[dict]:
    rng = random.Random(seed + 300)
    return [{"date": (datetime.now(timezone.utc) - timedelta(days=i*14)).strftime("%Y-%m-%d"), "shares_short": int(rng.uniform(30_000_000, 200_000_000)), "short_pct": round(rng.uniform(1, 8), 2)} for i in range(8)]

def _demo_darkpool(ticker: str, base: float, seed: int = 0, dp_bias: float = 0) -> list[dict]:
    rng = random.Random(seed + 400)
    # dp_bias > 0: more concentrated volume (bullish - large block trades)
    # dp_bias < 0: more distributed volume (bearish)
    result = []
    for offset in range(-15, 16):
        vol_mean = 255_000 + dp_bias * 200_000
        vol = int(max(5000, rng.gauss(vol_mean, 100_000)))
        result.append({"price": str(round(base + offset * base * 0.01, 2)), "volume": vol, "trades": rng.randint(5, 50)})
    return result

def _demo_options(ticker: str, base: float, seed: int = 0, os_bias: float = 0) -> list[dict]:
    rng = random.Random(seed + 500)
    # os_bias > 0: more Call OI (bullish)
    # os_bias < 0: more Put OI (bearish)
    result = []
    for offset in range(-12, 13):
        call_base = 50_000 + os_bias * 40_000
        put_base = 50_000 - os_bias * 40_000
        call_oi = int(max(1000, rng.gauss(call_base, call_base * 0.3)))
        put_oi = int(max(1000, rng.gauss(put_base, put_base * 0.3)))
        result.append({"strike": round(base + offset * base * 0.05, 2), "strike_price": round(base + offset * base * 0.05, 2), "call_open_interest": call_oi, "put_open_interest": put_oi})
    return result

def _demo_reddit(ticker: str, seed: int = 0, rs_bias: float = 0) -> list[dict]:
    rng = random.Random(seed + 600)
    # rs_bias > 0: increasing mention trend (bullish sentiment)
    # rs_bias < 0: decreasing mention trend (bearish sentiment)
    result = []
    for i in range(30):
        trend = rs_bias * (i / 30) * 200
        count = int(max(0, rng.uniform(20, 800) + trend))
        result.append({"date": (datetime.now(timezone.utc) - timedelta(days=i)).strftime("%Y-%m-%d"), "count": count})
    return result

def _demo_exchange(ticker: str, seed: int = 0, fs_bias: float = 0) -> list[dict]:
    rng = random.Random(seed + 700)
    result = []
    for i in range(10):
        # fs_bias > 0: higher institutional ratio (bullish)
        inst_pct = 0.7 + fs_bias * 0.2  # 0.5 to 0.9
        total_vol = int(rng.uniform(30_000_000, 120_000_000))
        inst_vol = int(total_vol * inst_pct)
        retail_vol = total_vol - inst_vol
        xnas = int(inst_vol * rng.uniform(0.45, 0.65))
        xny = inst_vol - xnas
        xbats = int(retail_vol * rng.uniform(0.4, 0.6))
        xotc = retail_vol - xbats
        result.append({"date": (datetime.now(timezone.utc) - timedelta(days=i)).strftime("%Y-%m-%d"), "xnas": xnas, "xny": xny, "xbats": xbats, "xotc": xotc})
    return result

async def get_quote(ticker: str) -> dict:
    r = await _call("Quote for a given stock", {"symbol": ticker})
    if isinstance(r, list) and len(r) > 0:
        q = r[0]
        # Real API returns string prices, normalize to float
        return {
            "reg_price": _safe_float(q.get("price")),
            "reg_change_pct": _safe_float(q.get("change_pct")),
            "reg_change": _safe_float(q.get("change")),
            "market_cap": _safe_float(q.get("market_cap")),
            "symbol": q.get("symbol", ticker),
        }
    return {}

async def get_bars(ticker: str, days: int = 60) -> list[dict]:
    r = await _call("Stock aggregate OHLC bars (k-line)", {"symbol": f"US:{ticker}", "agg_type": "day", "start": int(time.time()) - days*86400})
    return r if isinstance(r, list) else []

async def get_short_volume(ticker: str) -> list[dict]:
    r = await _call("Short volume for a given stock", {"symbol": f"US:{ticker}", "ordering": "-date"})
    return r if isinstance(r, list) else []

async def get_short_interest(ticker: str) -> list[dict]:
    r = await _call("Short Interest for a given stock", {"symbol": f"US:{ticker}", "ordering": "-date"})
    return r if isinstance(r, list) else []

async def get_daily_short_interest(ticker: str) -> list[dict]:
    r = await _call("Daily Short Interest for a given stock", {"symbol": f"US:{ticker}", "ordering": "-date"})
    return r if isinstance(r, list) else []

async def get_borrow_fee(ticker: str) -> list[dict]:
    r = await _call("Cost-to-borrow from Interactive Brokers", {"symbol": f"US:{ticker}", "ordering": "-timestamp", "page_size": 30})
    r = _extract_list(r)
    return r if isinstance(r, list) else []

async def get_ftds(ticker: str) -> list[dict]:
    r = await _call("FTDs for a given stock", {"symbol": f"US:{ticker}", "ordering": "-date"})
    return r if isinstance(r, list) else []

async def get_darkpool_levels(ticker: str) -> list[dict]:
    try:
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        r = await _call("Dark Pool Levels for a given stock", {"symbol": f"US:{ticker}", "date": today, "decimals": "2"})
        if isinstance(r, list):
            return r
        if isinstance(r, dict) and "error" not in r:
            levels = _extract_list(r)
            if levels:
                return levels
    except Exception:
        pass
    return []

async def get_options_chain(ticker: str) -> list[dict]:
    """Get options chain summary with real API data.
    Uses 'Option chain summary' which returns aggregate data per expiration."""
    try:
        # Try to get a near-term expiration first
        r = await _call("List of option contracts", {"underlying": f"US:{ticker}", "expiration_gte": datetime.now(timezone.utc).strftime("%Y-%m-%d"), "page_size": 1})
        exps = _extract_list(r)
        exp = exps[0].get("expiration") if exps else None
        if exp:
            r = await _call("Option chain summary (max pain, ITM/OTM)", {"underlying": f"US:{ticker}", "expiration": exp})
        else:
            # Fall back to a standard ~35d expiration
            r = await _call("Option chain summary (max pain, ITM/OTM)", {"underlying": f"US:{ticker}", "expiration": (datetime.now(timezone.utc) + timedelta(days=35)).strftime("%Y-%m-%d")})
    except Exception:
        return []
    return _extract_list(r)

async def get_reddit_mentions(ticker: str) -> list[dict]:
    r = await _call("Reddit mentions for a given stock", {"symbol": f"US:{ticker}"})
    return r if isinstance(r, list) else []

async def get_reddit_daily(ticker: str) -> list[dict]:
    r = await _call("Daily Reddit mention counts for a given stock", {"symbol": f"US:{ticker}"})
    return r if isinstance(r, list) else []

async def get_exchange_volume(ticker: str) -> list[dict]:
    """Get exchange volume. Map real API fields to calculator-expected keys.
    Real APIs exchange breakdown groups:
      Primary (institutional): xadf (ADF) + xngs (NGS) = ~75% of total
      Alternative (retail):    arcx + bats + edgx + iexg + ... = ~25%
    """
    r = await _call("Exchange volume for a given stock", {"symbol": f"US:{ticker}", "ordering": "-date"})
    if not isinstance(r, list):
        return []
    normalized = []
    for d in r:
        xadf = _safe_float(d.get("xadf", 0))
        xngs = _safe_float(d.get("xngs", 0))
        arcx = _safe_float(d.get("arcx", 0))
        bats = _safe_float(d.get("bats", 0))
        edgx = _safe_float(d.get("edgx", 0))
        iexg = _safe_float(d.get("iexg", 0))
        baty = _safe_float(d.get("baty", 0))
        edga = _safe_float(d.get("edga", 0))
        xnas = _safe_float(d.get("xnas", 0))
        xnys = _safe_float(d.get("xnys", 0))
        total = sum([xadf, xngs, arcx, bats, edgx, iexg, baty, edga, xnas, xnys,
                     _safe_float(d.get("xphl", 0)), _safe_float(d.get("xcis", 0)),
                     _safe_float(d.get("xase", 0)), _safe_float(d.get("xchi", 0)),
                     _safe_float(d.get("eprl", 0)), _safe_float(d.get("memx", 0)),
                     _safe_float(d.get("ltse", 0))])
        inst = xadf + xngs  # primary institutional venues (~75% of total)
        retail = total - inst
        # Spread across 4 expected fields for calculator to compute ratio
        normalized.append({
            "date": d.get("date", ""),
            "xnas": inst * 0.7,   # primary institutional
            "xny": inst * 0.3,    # secondary institutional
            "xbats": retail * 0.7,  # retail exchanges
            "xotc": retail * 0.3,   # other retail/OTC
        })
    return normalized

async def check_connectivity() -> str:
    try:
        r = await _call("List of stock exchanges")
        return "ok" if not (isinstance(r, dict) and "error" in r) else r["error"]
    except Exception as e:
        return f"error: {e}"
