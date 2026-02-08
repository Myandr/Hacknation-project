"""ASOS Produktsuche über RapidAPI asos10 (DataCrawler)."""
import logging
from typing import Any

import httpx
from schemas import ProductVariant
from config import RAPIDAPI_KEY, RAPIDAPI_ASOS_HOST, ASOS_SEARCH_ENDPOINT
from retailers.base import RetailerProduct

logger = logging.getLogger(__name__)

_BASE_URL = "https://{host}"
_API_V1 = "/api/v1"

# Cache für Countries/Categories (Prozess-Lebensdauer)
_categories_cache: list[dict[str, Any]] | None = None
_countries_cache: list[dict[str, Any]] | None = None


def clear_reference_caches() -> None:
    """Cache für Categories/Countries leeren (z. B. für Test/Reload)."""
    global _categories_cache, _countries_cache
    _categories_cache = None
    _countries_cache = None


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
        logger.warning("ASOS request failed: %s %s – %s", full_url, type(e).__name__, e)
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


def _flatten_categories(categories: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Kategorien mit children/subcategories zu einer flachen Liste auflösen."""
    out: list[dict[str, Any]] = []
    for c in categories:
        if not isinstance(c, dict):
            continue
        out.append(c)
        for key in ("children", "subcategories", "subCategories", "subcategoriesList", "categories"):
            nested = c.get(key)
            if isinstance(nested, list) and nested:
                out.extend(_flatten_categories(nested))
            elif isinstance(nested, dict):
                out.extend(_flatten_categories(list(nested.values())))
    return out


def get_categories() -> list[dict[str, Any]]:
    """GET /api/v1/getCategories. Gecacht. Verschachtelte Kategorien werden flach gemacht."""
    global _categories_cache
    if _categories_cache is not None:
        return _categories_cache
    data = _get(f"{_API_V1}/getCategories")
    if data is None:
        _categories_cache = []
        return _categories_cache
    if isinstance(data, list):
        _categories_cache = _flatten_categories([x for x in data if isinstance(x, dict)])
        return _categories_cache
    if isinstance(data, dict):
        raw = (
            data.get("categories")
            or data.get("categoryList")
            or data.get("data")
            or data.get("results")
            or data.get("navigation", {})
        )
        if isinstance(raw, dict):
            raw = raw.get("categories", raw.get("categoryList", list(raw.values())))
        if isinstance(raw, dict):
            raw = list(raw.values())
        if isinstance(raw, list):
            flat = _flatten_categories([x for x in raw if isinstance(x, dict)])
            _categories_cache = flat
        else:
            _categories_cache = []
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
    # cats kann Liste oder (bei alter API-Response) Dict sein – einheitlich iterierbar machen
    cat_list = list(cats.values()) if isinstance(cats, dict) else cats
    cat_lower = category.lower()
    for c in cat_list:
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
    first = (cat_list[0] if cat_list and isinstance(cat_list[0], dict) else None)
    return str(first.get("id", first.get("categoryId", ""))) if first else None


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


def _store_language_for_country(country_code: str) -> tuple[str, str]:
    """Liefert (store, language) für getProductDetails (z. B. US -> US, en-US)."""
    code = (country_code or "US").strip().upper()[:2]
    if code == "DE":
        return "DE", "de-DE"
    if code == "GB" or code == "UK":
        return "GB", "en-GB"
    return "US", "en-US"


def search_asos(
    query: str,
    category: str | None = None,
    limit: int = 10,
    country: str | None = None,
    currency: str | None = None,
) -> list[RetailerProduct]:
    """Sucht ASOS über RapidAPI asos10. country/currency aus KI-Brief (spec)."""
    if not RAPIDAPI_KEY or not RAPIDAPI_ASOS_HOST:
        logger.info("ASOS: RAPIDAPI_KEY oder RAPIDAPI_ASOS_HOST fehlt – überspringe.")
        return []

    country_code = (country or "DE").strip().upper() if country else "DE"
    if len(country_code) != 2:
        country_code = "DE"
    curr = (currency or "EUR").strip().upper() or "EUR"
    limit = min(max(1, limit), 48)
    base = _BASE_URL.format(host=RAPIDAPI_ASOS_HOST)

    # Parameter-Varianten (verschiedene APIs nutzen unterschiedliche Namen)
    param_sets: list[dict[str, str | int]] = []
    store_val, language_val = _store_language_for_country(country_code)
    size_schema = "US" if store_val == "US" else "EU"
    asos10_params = {"currency": curr, "store": store_val, "language": language_val, "sizeSchema": size_schema}

    if query and query.strip():
        q = query.strip()
        param_sets.append({"query": q, "limit": limit, "country": country_code})
        param_sets.append({"q": q, "limit": limit, "country": country_code})
        param_sets.append({"keyword": q, "limit": limit, "country": country_code})
        param_sets.append({"searchTerm": q, "limit": limit, "store": country_code})
        param_sets.append({"query": q, "pageSize": limit, "country": country_code})
        param_sets.append({**asos10_params, "query": q, "limit": limit})
        param_sets.append({**asos10_params, "q": q, "limit": limit})
    else:
        param_sets.append({"limit": limit, "country": country_code})
        param_sets.append({**asos10_params, "limit": limit})
        param_sets.append(asos10_params)

    # Endpoints: zuerst konfigurierter, dann typische asos10/getXxx-Varianten
    if ASOS_SEARCH_ENDPOINT:
        paths_to_try = [ASOS_SEARCH_ENDPOINT.strip().strip("/")]
    else:
        paths_to_try = [
            "/api/v1/getProductDetails",
            "/api/v1/getProducts",
            "/api/v1/getProductList",
            "/api/v1/searchProducts",
            "/api/v1/productSearch",
            "/api/v1/products",
            "/api/v1/product/list",
            "/api/v1/search",
            "/api/v1/product/search",
            "/v2/products/list",
        ]

    for path in paths_to_try:
        path_with_slash = path if path.startswith("/") else "/" + path
        url = base.rstrip("/") + path_with_slash
        for params in param_sets:
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
                logger.info("ASOS: %d Produkte von %s", len(products), path_with_slash)
                return products
    logger.info("ASOS: Keine Produkte – alle Endpoints fehlgeschlagen oder leere Antwort. Prüfe im Playground den exakten Pfad und setze ggf. ASOS_SEARCH_ENDPOINT in .env.")
    return []


def _parse_asos_response(data: dict | list, limit: int, currency: str = "EUR") -> list[RetailerProduct]:
    """Parst asos10-Response in RetailerProduct-Liste."""
    products: list[RetailerProduct] = []
    items: list[dict] = []

    if isinstance(data, list):
        items = [x for x in data if isinstance(x, dict)][:limit]
    elif isinstance(data, dict):
        raw = (
            data.get("products")
            or data.get("results")
            or data.get("items")
            or data.get("data")
            or data.get("list")
            or data.get("productList")
            or []
        )
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


def get_product_detail(
    product_id: str,
    currency: str = "USD",
    store: str | None = None,
    language: str | None = None,
    country_code: str | None = None,
) -> dict | None:
    """
    Einzelprodukt abrufen: GET /api/v1/getProductDetails.
    Parameternamen wie im RapidAPI-Playground: currency, store, language, sizeSchema.
    """
    if not product_id or not RAPIDAPI_KEY or not RAPIDAPI_ASOS_HOST:
        return None
    store_val, language_val = _store_language_for_country(country_code or store or "US")
    if store:
        store_val = store
    if language:
        language_val = language
    params: dict[str, str] = {
        "currency": (currency or "USD").upper(),
        "store": store_val,
        "language": language_val,
        "sizeSchema": "US" if store_val == "US" else "EU",
    }
    # Produkt-Id: API kann productId oder id erwarten
    for key in ("productId", "id", "articleId"):
        data = _get(f"{_API_V1}/getProductDetails", params={**params, key: product_id})
        if data is None:
            continue
        if isinstance(data, dict):
            return data
        if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
            return data[0]
    return None


def get_return_charges(country: str | None = None) -> dict | list | None:
    """Get Return Charges (optional für Checkout-Simulation)."""
    params = {"country": country or "DE"} if country else None
    return _get(f"{_API_V1}/getReturnCharges", params=params)


def _extract_product_list_from_response(data: Any) -> list[dict[str, Any]]:
    """Extrahiert eine Produktliste aus beliebigen API-Response-Formaten."""
    if data is None:
        return []
    if isinstance(data, list):
        return [x for x in data if isinstance(x, dict)]
    if not isinstance(data, dict):
        return []
    # Viele APIs nutzen unterschiedliche Keys
    for key in (
        "products", "results", "items", "productList", "list", "data", "response", "body", "value",
        "searchResults", "content", "itemList", "productListItems", "listing", "hits", "records",
    ):
        raw = data.get(key)
        if isinstance(raw, list):
            out = [x for x in raw if isinstance(x, dict)]
            if out:
                return out
        if isinstance(raw, dict):
            inner = _extract_product_list_from_response(raw)
            if inner:
                return inner
    # Einige APIs liefern { "data": [ { "product": {...} } ] } – product pro Eintrag
    for key in ("data", "results", "items"):
        raw = data.get(key)
        if isinstance(raw, list):
            out = []
            for x in raw:
                if not isinstance(x, dict):
                    continue
                p = x.get("product") or x.get("item") or x.get("productInfo") or x
                if isinstance(p, dict):
                    out.append(p)
                else:
                    out.append(x)
            if out:
                return out
    # RapidAPI asos10: manchmal { "status": bool, "message": list } – message = Fehler oder Liste
    if set(data.keys()) <= {"status", "message"}:
        msg = data.get("message")
        if isinstance(msg, list):
            dict_items = [x for x in msg if isinstance(x, dict)]
            if dict_items:
                return dict_items
    return []


def get_product_list(
    *,
    category_id: str | None = None,
    currency: str = "USD",
    country: str = "US",
    store: str | None = None,
    language_short: str = "en",
    size_schema: str = "US",
    limit: int = 50,
    offset: int = 0,
    sort: str = "recommended",
    price_min: int | float | None = None,
    price_max: int | float | None = None,
) -> list[dict[str, Any]]:
    """
    GET /api/v1/getProductList – Produktliste mit allen Parametern.
    Werte für categoryId, country, store etc. sollen aus den Referenzdaten
    (getCategories, getCountries) stammen, die die KI nutzt.
    """
    if not RAPIDAPI_KEY or not RAPIDAPI_ASOS_HOST:
        logger.warning("get_product_list: RAPIDAPI_KEY oder RAPIDAPI_ASOS_HOST fehlt")
        return []
    base = _BASE_URL.format(host=RAPIDAPI_ASOS_HOST)
    path = f"{_API_V1}/getProductList"
    url = base.rstrip("/") + path
    params: dict[str, str | int | float] = {
        "currency": (currency or "USD").upper(),
        "country": (country or "US").upper(),
        "store": (store or country or "US").upper(),
        "languageShort": language_short or "en",
        "sizeSchema": size_schema or "US",
        "limit": min(max(1, limit), 200),
        "offset": max(0, offset),
        "sort": sort or "recommended",
    }
    if category_id:
        params["categoryId"] = str(category_id)
    if price_min is not None:
        params["priceMin"] = price_min
    if price_max is not None:
        params["priceMax"] = price_max

    data = _get(url, params=params)
    if data is None:
        logger.info("get_product_list: API lieferte keine Daten (None). Prüfe RAPIDAPI_KEY und Endpoint.")
        return []

    out = _extract_product_list_from_response(data)
    if not out:
        logger.info(
            "get_product_list: Response enthält keine Produktliste. Typ=%s, Keys=%s",
            type(data).__name__,
            list(data.keys()) if isinstance(data, dict) else "n/a",
        )
    return out


def get_product_list_raw(
    **kwargs: Any,
) -> tuple[list[dict[str, Any]], Any]:
    """
    Wie get_product_list, gibt zusätzlich die Roh-Response zurück (für Debug).
    Returns: (product_list, raw_response).
    """
    if not RAPIDAPI_KEY or not RAPIDAPI_ASOS_HOST:
        return [], None
    base = _BASE_URL.format(host=RAPIDAPI_ASOS_HOST)
    path = f"{_API_V1}/getProductList"
    url = base.rstrip("/") + path
    params = {
        "currency": (kwargs.get("currency") or "USD").upper(),
        "country": (kwargs.get("country") or "US").upper(),
        "store": (kwargs.get("store") or kwargs.get("country") or "US").upper(),
        "languageShort": kwargs.get("language_short") or "en",
        "sizeSchema": kwargs.get("size_schema") or "US",
        "limit": min(max(1, kwargs.get("limit", 50)), 200),
        "offset": max(0, kwargs.get("offset", 0)),
        "sort": kwargs.get("sort") or "recommended",
    }
    if kwargs.get("category_id"):
        params["categoryId"] = str(kwargs["category_id"])
    if kwargs.get("price_min") is not None:
        params["priceMin"] = kwargs["price_min"]
    if kwargs.get("price_max") is not None:
        params["priceMax"] = kwargs["price_max"]
    data = _get(url, params=params)
    return _extract_product_list_from_response(data) if data else [], data
