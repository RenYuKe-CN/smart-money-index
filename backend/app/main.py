from __future__ import annotations
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import smi, config, health
from app.services.config_store import set_default_watchlist

app = FastAPI(title="Smart Money Index", description="Institutional sentiment dashboard", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.include_router(smi.router)
app.include_router(config.router)
app.include_router(health.router)

@app.on_event("startup")
async def startup():
    set_default_watchlist()
    print("🚀 SMI Backend started")
