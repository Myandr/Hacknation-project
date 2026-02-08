"""ASOS Produktsuche über RapidAPI asos10 (DataCrawler)."""
import logging
from typing import Any

import httpx
from schemas import ProductVariant
from config import RAPIDAPI_KEY, RAPIDAPI_ASOS_HOST
from retailers.base import RetailerProduct

logger = logging.getLogger(__name__)

_BASE_URL = "https://{host}"
_API_V1 = "/api/v1"

# Cache für Countries/Categories (Prozess-Lebensdauer)
_categories_cache: list[dict[str, Any]] | None = None
_countries_cache: list[dict[str, Any]] | None = None


def _headers() -> dict[str, str]:
    return {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": RAPIDAPI_ASOS_HOST,
    }


def _get(url: str, params: dict | None = None) -> dict | list | None:
    """GET-Anfrage an asos10; bei Fehler None, kein Throw."""
    if not RAPIDAPI_KEY or not RAPIDAPI_ASOS_HOST:
        return None
    base = _BASE_URL.format(host=RAPIDAPI_ASOS_HOST)
    full_url = url if url.startswith("http") else base.rstrip("/") + url
    try:
        with httpx.Client(timeout=15.0) as client:
            resp = client.get(full_url, params=params or {}, headers=_headers())
            resp.raise_for_status()
            return resp.json()
    except (httpx.HTTPError, ValueError) as e:
        logger.debug("ASOS request failed: %s %s", full_url, type(e).__name__)
        return None


def get_countries() -> list[dict[str, Any]]:
    """GET /api/v1/getCountries. Gecacht."""
    global _countries_cache
    if _countries_cache is not None:
        return _countries_cache
    data = _get(f"{_API_V1}/getCountries")
    if data is None:
        _countries_cache = []
        return _countries_cache
    if isinstance(data, list):
        _countries_cache = data
    elif isinstance(data, dict):
        _countries_cache = data.get("countries", data.get("data", data.get("results", [])))
    else:
        _countries_cache = []
    return _countries_cache


def get_categories() -> list[dict[str, Any]]:
    """GET /api/v1/getCategories. Gecacht."""
    global _categories_cache
    if _categories_cache is not None:
        return _categories_cache
    data = _get(f"{_API_V1}/getCategories")
    if data is None:
        _categories_cache = []
        return _categories_cache
    if isinstance(data, list):
        _categories_cache = data
    elif isinstance(data, dict):
        _categories_cache = data.get("categories", data.get("data", data.get("results", [])))
    else:
        _categories_cache = []
    return _categories_cache


def _category_to_api_id(category: str | None) -> str | None:
    """Mapping Brief-Kategorie (clothing/food/both/other) auf API-Kategorie-ID."""
    if not category or category == "other":
        return None
    cats = get_categories()
    if not cats:
        return None
    cat_lower = category.lower()
    for c in cats:
        if not isinstance(c, dict):
            continue
        name = (c.get("name") or c.get("title") or "").lower()
        cid = c.get("id") or c.get("categoryId") or c.get("code")
        if not cid:
            continue
        if cat_lower == "clothing" and ("cloth" in name or "women" in name or "men" in name or "wear" in name):
            return str(cid)
        if cat_lower == "food" and ("food" in name or "grocery" in name):
            return str(cid)
        if cat_lower == "both":
            return str(cid)
    return str(cats[0].get("id", cats[0].get("categoryId", ""))) if cats and isinstance(cats[0], dict) else None


def _normalize_country_code(spec_country: str | None) -> str:
    """Land aus Brief in API-Code (z. B. DE, US)."""
    if not spec_country or not spec_country.strip():
        return "DE"
    s = spec_country.strip().upper()
    if len(s) == 2:
        return s
    countries = get_countries()
    for c in countries:
        if not isinstance(c, dict):
            continue
        name = (c.get("name") or c.get("countryName") or "").strip()
        code = (c.get("code") or c.get("countryCode") or c.get("id") or "").strip().upper()
        if s in (name.upper(), code) or (len(code) == 2 and s == code):
            return code if len(code) == 2 else "DE"
    return "DE"


def search_asos(
    query: str,
    category: str | None = None,
    limit: int = 10,
    country: str | None = None,
    currency: str | None = None,
) -> list[RetailerProduct]:
    """Sucht ASOS über RapidAPI asos10. country/currency aus KI-Brief (spec)."""
    if not RAPIDAPI_KEY or not RAPIDAPI_ASOS_HOST:
        return []

    country_code = _normalize_country_code(country) if country else "DE"
    curr = (currency or "EUR").strip().upper() or "EUR"
    limit = min(max(1, limit), 48)

    base = _BASE_URL.format(host=RAPIDAPI_ASOS_HOST)
    params: dict[str, str | int] = {
        "limit": limit,
        "country": country_code,
    }
    if query and query.strip():
        params["query"] = query.strip()
    category_id = _category_to_api_id(category)
    if category_id:
        params["categoryId"] = category_id

    # asos10: typische Pfade für Produktsuche (Playground ggf. anpassen)
    for path in ("/api/v1/searchProducts", "/api/v1/products", "/api/v1/product/list"):
        url = base.rstrip("/") + path
        try:
            with httpx.Client(timeout=15.0) as client:
                resp = client.get(url, params=params, headers=_headers())
                if resp.status_code != 200:
                    continue
                data = resp.json()
        except (httpx.HTTPError, ValueError):
            continue
        products = _parse_asos_response(data, limit, currency=curr)
        if products:
            return products
    return []


def _parse_asos_response(data: dict | list, limit: int, currency: str = "EUR") -> list[RetailerProduct]:
    """Parst asos10-Response in RetailerProduct-Liste."""
    products: list[RetailerProduct] = []
    items: list[dict] = []

    if isinstance(data, list):
        items = [x for x in data if isinstance(x, dict)][:limit]
    elif isinstance(data, dict):
        raw = data.get("products") or data.get("results") or data.get("items") or data.get("data") or []
        items = [x for x in (raw if isinstance(raw, list) else []) if isinstance(x, dict)][:limit]
    if not items:
        return []

    curr = currency or "EUR"
    for p in items:
        pid = str(p.get("id") or p.get("productId") or p.get("articleNumber") or p.get("articleId") or "")
        if not pid:
            continue
        price_data = p.get("price") or p.get("priceInfo") or p.get("currentPrice") or {}
        if isinstance(price_data, (int, float)):
            price = float(price_data)
        else:
            price = float(price_data.get("current", price_data.get("value", price_data.get("amount", 0))) or 0)
        title = (p.get("name") or p.get("title") or p.get("productTitle") or p.get("productName") or "Unbekannt").strip() or "Unbekannt"
        variants = []
        raw_variants = p.get("variants") or p.get("sizes") or p.get("variation") or []
        if not isinstance(raw_variants, list):
            raw_variants = []
        for v in raw_variants:
            if isinstance(v, dict):
                variants.append(ProductVariant(size=v.get("size"), color=v.get("color"), sku=v.get("sku")))
            elif isinstance(v, str):
                variants.append(ProductVariant(size=v))

        delivery = p.get("delivery") or p.get("estimatedDeliveryDays") or p.get("deliveryDays")
        if isinstance(delivery, dict):
            delivery_days = delivery.get("days") or delivery.get("estimatedDeliveryDays")
        else:
            delivery_days = int(delivery) if delivery is not None else None
        delivery_days = delivery_days if isinstance(delivery_days, int) and delivery_days is not None else None

        image_url = p.get("imageUrl") or p.get("image") or p.get("thumbnail") or p.get("productImage") or ""
        product_url = p.get("url") or p.get("link") or p.get("productUrl") or ""

        products.append(RetailerProduct(
            retailer_id="asos",
            product_id=pid,
            title=title,
            price=price,
            currency=curr,
            delivery_estimate_days=delivery_days,
            image_url=image_url or None,
            product_url=product_url or None,
            variants=variants,
            raw=p,
        ))
    return products


def get_product_detail(product_id: str) -> dict | None:
    """Einzelprodukt abrufen (falls asos10 einen Detail-Endpoint hat)."""
    if not product_id or not RAPIDAPI_KEY or not RAPIDAPI_ASOS_HOST:
        return None
    base = _BASE_URL.format(host=RAPIDAPI_ASOS_HOST)
    data = _get(f"{base.rstrip('/')}/api/v1/product", params={"id": product_id})
    if isinstance(data, dict):
        return data
    if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
        return data[0]
    return None


def get_return_charges(country: str | None = None) -> dict | list | None:
    """Get Return Charges (optional für Checkout-Simulation)."""
    params = {"country": country or "DE"} if country else None
    return _get(f"{_API_V1}/getReturnCharges", params=params)
