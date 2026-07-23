from __future__ import annotations
from statistics import mean
def score(data: list[dict], weight: float = 0.20) -> dict:
    if not data: return {"score": 50, "trend": "flat", "detail": "暂无短仓数据"}
    ratios = []
    for d in data[:30]:
        st = float(d.get("st", d.get("short_volume", 0)))
        rt = float(d.get("rt", d.get("total_volume", 1)))
        ratios.append(st / rt if rt > 0 else 0)
    if not ratios: return {"score": 50, "trend": "flat", "detail": "短仓比数据为空"}
    recent = mean(ratios[:5]) if len(ratios) >= 5 else mean(ratios)
    older = mean(ratios[5:15]) if len(ratios) >= 15 else mean(ratios)
    change = (older - recent) / older * 100 if older > 0 else 0
    score_val = max(0, min(100, 50 + change * 2))
    trend = "up" if change > 5 else "down" if change < -5 else "flat"
    return {"score": round(score_val, 1), "trend": trend, "detail": f"短仓比变化 {round(change, 1)}%"}
