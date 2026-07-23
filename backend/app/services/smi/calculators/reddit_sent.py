from __future__ import annotations
from statistics import mean
def score(data: list[dict], weight: float = 0.10) -> dict:
    if not data: return {"score": 50, "trend": "flat", "detail": "暂无 Reddit 数据"}
    counts = [float(d.get("count", d.get("mention_count", 0))) for d in data if d.get("count", d.get("mention_count", 0)) is not None]
    if not counts: return {"score": 50, "trend": "flat", "detail": "提及数为空"}
    recent = mean(counts[:5]) if len(counts) >= 5 else mean(counts)
    older = mean(counts[5:15]) if len(counts) >= 15 else mean(counts)
    change = (recent - older) / older * 100 if older > 0 else 0
    score_val = max(0, min(100, 50 - change * 0.3))
    trend = "down" if change > 20 else "up" if change < -20 else "flat"
    return {"score": round(score_val, 1), "trend": trend, "detail": f"Reddit 变化 {round(change, 1)}%"}
