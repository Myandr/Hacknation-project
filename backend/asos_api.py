"""
ASOS-Produktsuche über RapidAPI.
Nutzt die gespeicherte Kategorie (und ggf. weitere Anforderungen) für die Suche.
"""

import os
from typing import Any

import httpx
from dotenv import load_dotenv

load_dotenv()

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
ASOS_HOST = "asos10.p.rapidapi.com"
BASE_URL = "https://asos10.p.rapidapi.com/api/v1/getProductListBySearchTerm"


# Kategorie (von der KI) -> Suchbegriff für ASOS (Mode-Shop, daher vor allem Kleidung)
CATEGORY_TO_SEARCH: dict[str, str] = {
    "clothing": "clothing",
    "food": "food",
    "both": "clothing",
    "other": "fashion",
}


def _default_search_term(category: str | None) -> str:
    """Leitet aus der von der KI gespeicherten Kategorie den ASOS-Suchbegriff ab."""
    if category and category.strip():
        key = category.strip().lower()
        if key in CATEGORY_TO_SEARCH:
            return CATEGORY_TO_SEARCH[key]
        return key  # Unbekannte Kategorie direkt als Suchbegriff
    return "fashion"


def search_products_by_category(
    category: str | None,
    *,
    currency: str = "USD",
    country: str = "US",
    store: str = "US",
    limit: int = 10,
    offset: int = 0,
    **kwargs: Any,
) -> dict[str, Any]:
    """
    Sucht ASOS-Produkte anhand der **von der KI gespeicherten Kategorie**.
    category: Wert aus ShoppingRequirement.category (clothing, food, both, other).
    Der Suchbegriff wird daraus abgeleitet (z. B. both -> clothing).
    """
    search_term = _default_search_term(category)
    return search_products(
        search_term,
        currency=currency,
        country=country,
        store=store,
        limit=limit,
        offset=offset,
        **kwargs,
    )


def search_products(
    search_term: str,
    *,
    currency: str = "USD",
    country: str = "US",
    store: str = "US",
    language_short: str = "en",
    size_schema: str = "US",
    limit: int = 50,
    offset: int = 0,
    sort: str = "recommended",
) -> dict[str, Any]:
    """
    Ruft die ASOS RapidAPI auf und gibt die Rohantwort zurück.
    """
    if not RAPIDAPI_KEY:
        return {
            "error": "RAPIDAPI_KEY nicht gesetzt",
            "products": [],
        }

    params = {
        "searchTerm": search_term,
        "currency": currency,
        "country": country,
        "store": store,
        "languageShort": language_short,
        "sizeSchema": size_schema,
        "limit": limit,
        "offset": offset,
        "sort": sort,
    }

    headers = {
        "x-rapidapi-host": ASOS_HOST,
        "x-rapidapi-key": RAPIDAPI_KEY,
    }

    with httpx.Client(timeout=30.0) as client:
        resp = client.get(BASE_URL, params=params, headers=headers)

    if resp.status_code != 200:
        return {
            "error": f"ASOS API Fehler: {resp.status_code}",
            "products": [],
            "raw": resp.text[:500] if resp.text else None,
        }

    data = resp.json()
    # API kann unterschiedliche Strukturen haben; Produktliste oft unter "products" oder direkt als Liste
    if isinstance(data, list):
        return {"products": data, "count": len(data)}
    if isinstance(data, dict):
        products = data.get("products", data.get("productList", data.get("data", [])))
        if not isinstance(products, list):
            products = [data] if data else []
        return {
            "products": products,
            "count": len(products),
            **{k: v for k, v in data.items() if k not in ("products", "productList", "data")},
        }
    return {"products": [], "count": 0}
