import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "SENTINEL GRID - Unified Federated Video Intelligence"
    API_V1_STR: str = "/api"
    SECRET_KEY: str = "SENTINEL_GRID_SUPER_SECRET_KEY_PRODUCTION_GRADE_2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/sentinel_grid"
    REDIS_URL: str = "redis://localhost:6379/0"
    MEDIAMTX_HLS_BASE: str = "http://localhost:8888"
    MEDIAMTX_WEBRTC_BASE: str = "http://localhost:8889"
    CORS_ORIGINS: List[str] = ["*"]
    EVIDENCE_DIR: str = "./evidence_storage"
    
    # Stream & Reconnection parameters (ADR-007 / Rules)
    INITIAL_RECONNECT_DELAY_SEC: float = 2.0
    MAX_RECONNECT_DELAY_SEC: float = 30.0
    RECONNECT_BACKOFF_FACTOR: float = 1.5

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow"
    )

settings = Settings()
os.makedirs(settings.EVIDENCE_DIR, exist_ok=True)
os.makedirs(os.path.join(settings.EVIDENCE_DIR, "snapshots"), exist_ok=True)
os.makedirs(os.path.join(settings.EVIDENCE_DIR, "clips"), exist_ok=True)
