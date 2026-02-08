"""Konfiguration aus Umgebungsvariablen."""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")

GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

RAPIDAPI_KEY: str = os.getenv("RAPIDAPI_KEY", "")
RAPIDAPI_ASOS_HOST: str = os.getenv("RAPIDAPI_ASOS_HOST", "asos10.p.rapidapi.com")
# Optional: exakter Such-Endpoint aus dem RapidAPI-Playground (z.B. /api/v1/getProducts)
ASOS_SEARCH_ENDPOINT: str | None = os.getenv("ASOS_SEARCH_ENDPOINT") or None

DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./agentic_commerce.db")
