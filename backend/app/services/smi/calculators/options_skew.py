from __future__ import annotations
def score(data: list[dict], weight: float = 0.20) -> dict:
    if not data: return {"score": 50, "trend": "flat", "detail": "暂无期权数据"}
    # Handle both per-strike format (call_open_interest) and aggregate format (call_itm+call_otm)
    call = 0
    put = 0
    for d in data:
        call_oi_raw = d.get("call_open_interest", d.get("call_oi"))
        put_oi_raw = d.get("put_open_interest", d.get("put_oi"))
        if call_oi_raw is not None and put_oi_raw is not None:
            call += float(call_oi_raw)
            put += float(put_oi_raw)
        else:
            # Aggregate format from real API: call_itm + call_otm, put_itm + put_otm
            call += float(d.get("call_itm", d.get("call_oi", 0))) + float(d.get("call_otm", 0))
            put += float(d.get("put_itm", d.get("put_oi", 0))) + float(d.get("put_otm", 0))
    if call + put == 0: return {"score": 50, "trend": "flat", "detail": "OI 为零"}
    ratio = call / (call + put)
    score_val = ratio * 100
    trend = "up" if ratio > 0.6 else "down" if ratio < 0.4 else "flat"
    return {"score": round(score_val, 1), "trend": trend, "detail": f"Call 占比 {round(ratio*100, 1)}%"}
