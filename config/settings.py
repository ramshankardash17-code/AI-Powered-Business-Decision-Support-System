"""
Application Settings & Configuration
Enterprise AI Business Decision Intelligence Platform
"""
import os
from pathlib import Path
from typing import List
from pydantic import BaseModel
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

class Settings(BaseModel):
    # App Information
    PROJECT_NAME: str = "Enterprise AI Business Decision Intelligence Platform"
    API_VERSION: str = "1.0.0"
    DEBUG: bool = True
    BASE_DIR: Path = BASE_DIR

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql+psycopg2://postgres:postgres@localhost:5432/ecommerce_bi"
    )
    USE_SQLITE_FALLBACK: bool = os.getenv("USE_SQLITE_FALLBACK", "true").lower() == "true"
    SQLITE_DB_PATH: Path = BASE_DIR / os.getenv("SQLITE_DB_PATH", "data/ecommerce_bi.db")

    # Data & Model Directories
    DATA_DIR: Path = BASE_DIR / "data"
    DOCUMENTS_DIR: Path = BASE_DIR / "data" / "documents"
    MODELS_DIR: Path = BASE_DIR / "data" / "models"
    REPORTS_DIR: Path = BASE_DIR / "data" / "reports"

    # AI & LLM Settings
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "mock_heuristic")

    # Thresholds
    DATA_QUALITY_THRESHOLD: float = float(os.getenv("DATA_QUALITY_THRESHOLD", "85.0"))
    DRIFT_ALERT_THRESHOLD: float = float(os.getenv("DRIFT_ALERT_THRESHOLD", "0.15"))

    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8000",
        "*"
    ]

    class Config:
        case_sensitive = True

settings = Settings()

# Ensure critical directories exist
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
settings.DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
settings.MODELS_DIR.mkdir(parents=True, exist_ok=True)
settings.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
