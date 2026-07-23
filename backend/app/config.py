from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    backend_port: int = 8002
    clawby_api_key: str = ""
    clawby_base_url: str = "https://api.openclawby.com"
    data_dir: str = str(Path(__file__).resolve().parent / "data")

    @property
    def config_path(self) -> Path:
        return Path(self.data_dir) / "config.json"

    def model_post_init(self, __context: Any) -> None:
        Path(self.data_dir).mkdir(parents=True, exist_ok=True)


settings = Settings()


def load_json(path: Path) -> list | dict:
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {}


def save_json(path: Path, data: list | dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
