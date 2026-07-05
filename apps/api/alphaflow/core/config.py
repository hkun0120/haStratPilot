from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT_DIR = Path(__file__).resolve().parents[4]


class Settings(BaseSettings):
    app_name: str = "StratPilot"
    volc_ark_api_key: str | None = None
    volc_ark_model: str = "doubao-seed-2-1-pro-260628"
    volc_ark_base_url: str = "https://ark.cn-beijing.volces.com/api/v3"
    qveris_api_key: str | None = None
    qveris_base_url: str = "https://qveris.ai/api/v1"
    data_cache_dir: Path = ROOT_DIR / "data" / "cache"
    ledger_path: Path = ROOT_DIR / "apps" / "api" / "alphaflow" / "storage" / "ledger.json"
    runtime_config_path: Path = ROOT_DIR / "apps" / "api" / "alphaflow" / "storage" / "runtime_config.json"
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    model_config = SettingsConfigDict(
        env_file=(
            ROOT_DIR / ".env",
            ROOT_DIR / ".env.local",
            ROOT_DIR / ".env.example",
            ROOT_DIR / ".env copy.example",
        ),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.data_cache_dir.mkdir(parents=True, exist_ok=True)
    settings.ledger_path.parent.mkdir(parents=True, exist_ok=True)
    settings.runtime_config_path.parent.mkdir(parents=True, exist_ok=True)
    return settings
