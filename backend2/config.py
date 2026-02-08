"""Konfiguration aus Umgebungsvariablen."""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")

GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

SERPAPI_KEY: str = os.getenv("SERPAPI_KEY", "")

DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./agentic_commerce.db")
