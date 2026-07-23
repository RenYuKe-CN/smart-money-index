from __future__ import annotations
from fastapi import APIRouter
from app.services import config_store as cfg
from app.services import clawby as c

router = APIRouter(tags=["health"])

@router.get("/api/health")
async def health():
    status = await c.check_connectivity()
    return {"status": "ok", "clawby_status": status, "version": "0.1.0"}
