from __future__ import annotations
from app.config import settings, load_json, save_json

def load_config() -> dict:
    cfg = load_json(settings.config_path)
    if not cfg:
        cfg = {"clawby_api_key": settings.clawby_api_key, "watchlist": ["AAPL", "NVDA", "TSLA", "MSFT", "AMZN"]}
        save_config(cfg)
    return cfg

def save_config(data: dict) -> None:
    save_json(settings.config_path, data)

def get_clawby_key() -> str:
    return load_config().get("clawby_api_key", settings.clawby_api_key)

def update_clawby_key(key: str) -> None:
    cfg = load_config()
    cfg["clawby_api_key"] = key
    save_config(cfg)

def get_watchlist() -> list[str]:
    return load_config().get("watchlist", ["AAPL", "NVDA", "TSLA", "MSFT", "AMZN"])

def update_watchlist(tickers: list[str]) -> None:
    cfg = load_config()
    cfg["watchlist"] = tickers
    save_config(cfg)

def set_default_watchlist() -> None:
    cfg = load_config()
    if "watchlist" not in cfg:
        cfg["watchlist"] = ["AAPL", "NVDA", "TSLA", "MSFT", "AMZN"]
        save_config(cfg)
