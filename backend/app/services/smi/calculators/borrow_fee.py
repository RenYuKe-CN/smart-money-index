from __future__ import annotations
def score(data: list[dict], weight: float = 0.15) -> dict:
    if not data: return {"score": 50, "trend": "flat", "detail": "暂无费率数据"}
    rates = [float(d.get("borrow_rate", d.get("fee", 0))) for d in data if d.get("borrow_rate", d.get("fee", 0))]
    if not rates: return {"score": 50, "trend": "flat", "detail": "费率为空"}
    cur = rates[0]
    score_val = max(0, min(100, 50 + (min(cur, 20) - 1) * 10 if cur > 1 else 50 - (1 - cur) * 20))
    trend = "up" if cur > 3 else "down" if cur < 1.5 else "flat"
    return {"score": round(score_val, 1), "trend": trend, "detail": f"借券费率 {round(cur, 2)}%"}
