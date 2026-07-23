from __future__ import annotations
from statistics import mean
from typing import Any

def score(data: list[dict], weight: float = 0.25, ticker_seed: float = 0.0) -> dict:
    if not data: return {"score": 50, "trend": "flat", "detail": "暂无暗池数据"}
    vols = [abs(float(v)) for d in data if (v := d.get("volume", d.get("vol", 0)))]
    if not vols: return {"score": 50, "trend": "flat", "detail": "成交量数据为空"}
    # Use percentile-based threshold: top 20% of volumes = "large" trades
    sorted_vols = sorted(vols)
    threshold_idx = int(len(sorted_vols) * 0.8)
    threshold = sorted_vols[threshold_idx] if threshold_idx < len(sorted_vols) else sorted_vols[-1]
    large = sum(v for v in vols if v >= threshold)
    ratio = large / sum(vols) if sum(vols) > 0 else 0
    # score between 0-100: 0% ratio = 0, 50% ratio = 100
    score_val = min(100, max(0, ratio * 100 * 2))
    trend = "up" if ratio > 0.3 else "down" if ratio < 0.1 else "flat"
    return {"score": round(score_val, 1), "trend": trend, "detail": f"暗池大单占比 {round(ratio*100, 1)}%"}
