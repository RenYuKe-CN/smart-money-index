from __future__ import annotations
def score(data: list[dict], weight: float = 0.10) -> dict:
    if not data: return {"score": 50, "trend": "flat", "detail": "暂无交易所数据"}
    ratios = []
    for d in data[:10]:
        xnas = float(d.get("xnas", 0))
        xny = float(d.get("xny", 0))
        total = xnas + xny + float(d.get("xbats", 0)) + float(d.get("xotc", 0))
        ratios.append((xnas + xny) / total if total > 0 else 0.5)
    ratio = ratios[0] if ratios else 0.5
    score_val = max(0, min(100, ratio * 100))
    trend = "up" if ratio > 0.7 else "down" if ratio < 0.4 else "flat"
    return {"score": round(score_val, 1), "trend": trend, "detail": f"机构占比 {round(ratio*100, 1)}%"}
