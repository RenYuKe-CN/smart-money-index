from __future__ import annotations
from fastapi import APIRouter, HTTPException
from app.models.schemas import SMIResponse, SMIDetailResponse, ScannerResponse
from app.services.smi.engine import get_cached_smi
from app.services.smi.scanner import scan_market

router = APIRouter(prefix="/api", tags=["smi"])


@router.post("/smi/batch")
async def get_smi_batch(body: dict):
    from app.services.smi.engine import get_cached_smi
    tickers = body.get("tickers", [])
    results = {}
    for ticker in tickers:
        try:
            result = await get_cached_smi(ticker.upper())
            results[ticker.upper()] = {"smi": result["smi"], "level": result["level"]}
        except Exception:
            results[ticker.upper()] = {"smi": 50, "level": "neutral"}
    return results

@router.get("/smi/market-overview")
async def get_market_overview():
    from app.services.smi.scanner import scan_market
    scanner = await scan_market()
    counts = {"bearish": 0, "neutral": 0, "bullish": 0, "extreme_bearish": 0, "extreme_bullish": 0}
    for item in scanner["items"]:
        level = item.get("level", "neutral")
        for key in counts:
            if level == key or level.startswith(key):
                counts[key] += 1
                break
        else:
            counts["neutral"] += 1
    return {"counts": counts, "market_smi": scanner["market_smi"], "total": scanner["total"]}
@router.get("/smi/{ticker}", response_model=SMIResponse)
async def get_smi(ticker: str):
    result = await get_cached_smi(ticker.upper())
    return SMIResponse(
        ticker=result["ticker"],
        smi=result["smi"],
        level=result["level"],
        change_1d=result.get("change_1d", 0),
        dimensions=result.get("dimensions", []),
        signal=result.get("signal", "none") if result.get("signal") != "none" else None,
        signal_detail=result.get("signal_detail", ""),
        updated_at=result.get("updated_at", ""),
    )

@router.get("/smi/{ticker}/detail", response_model=SMIDetailResponse)
async def get_smi_detail(ticker: str, refresh: bool = False):
    result = await get_cached_smi(ticker.upper(), force_refresh=refresh)
    return SMIDetailResponse(
        ticker=result["ticker"],
        smi=result["smi"],
        level=result["level"],
        change_1d=result.get("change_1d", 0),
        dimensions=result.get("dimensions", []),
        signal=result.get("signal", "none") if result.get("signal") != "none" else None,
        signal_detail=result.get("signal_detail", ""),
        updated_at=result.get("updated_at", ""),
        history=result.get("history", []),
        price_current=result.get("price", 0),
        price_change_pct=result.get("price_change", 0),
    )

@router.get("/scanner", response_model=ScannerResponse)
async def get_scanner():
    return await scan_market()
