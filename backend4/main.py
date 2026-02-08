import os
from fastapi import FastAPI, Query
from serpapi import GoogleSearch
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Backend4 – SerpAPI Google Search")


@app.get("/")
def root():
    return {"message": "Backend4 API – nutze /search?q=deine_suche für Google-Suchergebnisse"}


@app.get("/search")
def google_search(q: str = Query(..., description="Suchbegriff für Google")):
    """Einfache API-Anfrage an SerpAPI für die Google Search API."""
    api_key = os.getenv("SERPAPI_API_KEY")
    if not api_key:
        return {"error": "SERPAPI_API_KEY fehlt in .env"}

    params = {
        "q": q,
        "engine": "google",
        "api_key": api_key,
        "hl": "de",
        "gl": "de",
    }
    search = GoogleSearch(params)
    results = search.get_dict()

    organic = results.get("organic_results", [])
    return {
        "query": q,
        "result_count": len(organic),
        "results": [
            {"title": r.get("title"), "link": r.get("link"), "snippet": r.get("snippet")}
            for r in organic[:10]
        ],
    }
