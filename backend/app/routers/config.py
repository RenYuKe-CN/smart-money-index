from __future__ import annotations
from fastapi import APIRouter, HTTPException
from app.models.schemas import ConfigResponse
from app.services import config_store as cfg
from app.services import clawby as c

router = APIRouter(prefix="/api/config", tags=["config"])

@router.get("")
async def get_config():
    config = cfg.load_config()
    status = await c.check_connectivity()
    return {
        "clawby_configured": bool(config.get("clawby_api_key")),
        "clawby_status": status,
        "watchlist": config.get("watchlist", []),
        "api_key_preview": config.get("clawby_api_key", "")[:10] + "..." if len(config.get("clawby_api_key", "")) > 12 else "",
    }

@router.put("/clawby-key")
async def update_clawby_key(body: dict):
    key = body.get("api_key", "").strip()
    if not key:
        raise HTTPException(400, "API key cannot be empty")
    cfg.update_clawby_key(key)
    return {"status": "ok"}

@router.put("/watchlist")
async def update_watchlist(body: dict):
    tickers = body.get("tickers", [])
    if not tickers:
        raise HTTPException(400, "Watchlist cannot be empty")
    cfg.update_watchlist(tickers)
    return {"status": "ok"}



@router.get("/llm-config")
async def get_llm_config():
    cfg = __import__("app.services.config_store", fromlist=["load_config"]).load_config()
    return {
        "provider_type": cfg.get("llm_provider_type", ""),
        "api_base": cfg.get("llm_api_base", ""),
        "api_key_preview": cfg.get("llm_api_key", "")[:10] + "..." if len(cfg.get("llm_api_key", "")) > 12 else "",
        "model": cfg.get("llm_model", ""),
        "configured": bool(cfg.get("llm_api_key")),
    }

@router.put("/llm-config")
async def update_llm_config(body: dict):
    cfg = __import__("app.services.config_store", fromlist=["load_config"]).load_config()
    for key in ["llm_provider_type", "llm_api_base", "llm_api_key", "llm_model"]:
        if key in body:
            cfg[key] = body[key]
    __import__("app.services.config_store", fromlist=["save_config"]).save_config(cfg)
    return {"status": "ok"}
@router.get("/test-clawby")
async def test_clawby():
    status = await c.check_connectivity()
    return {"success": status == "ok", "message": status}
