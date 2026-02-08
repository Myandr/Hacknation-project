"""ASOS Produktsuche über RapidAPI."""
import httpx
from schemas import ProductVariant
from config import RAPIDAPI_KEY, RAPIDAPI_ASOS_HOST
from retailers.base import RetailerProduct


def search_asos(
    query: str,
    category: str | None = None,
    limit: int = 10,
) -> list[RetailerProduct]:
    """Sucht ASOS über RapidAPI. Bei fehlendem Key oder anderem Host: leere Liste."""
    if not RAPIDAPI_KEY or not RAPIDAPI_ASOS_HOST:
        return []

    base_url = f"https://{RAPIDAPI_ASOS_HOST}"
    # Typische RapidAPI-ASOS Endpoints: /products/list oder /v2/products/list
    url = f"{base_url}/products/list"
    params = {
        "offset": "0",
        "limit": str(min(limit, 48)),
        "country": "DE",
        "lang": "de-DE",
        "store": "DE",
    }
    if query:
        params["q"] = query
    if category:
        params["categoryId"] = _category_to_asos_id(category)

    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": RAPIDAPI_ASOS_HOST,
    }

    with httpx.Client(timeout=15.0) as client:
        try:
            resp = client.get(url, params=params, headers=headers)
            resp.raise_for_status()
            data = resp.json()
        except (httpx.HTTPError, Exception):
            return []

    return _parse_asos_response(data, limit)


def _category_to_asos_id(category: str) -> str:
    """Kategorie zu ASOS categoryId (falls API das erwartet)."""
    m = {"clothing": "4208", "food": "", "both": ""}
    return m.get(category, "")


def _parse_asos_response(data: dict, limit: int) -> list[RetailerProduct]:
    """Parst verschiedene mögliche RapidAPI-ASOS Antwortformate."""
    products: list[RetailerProduct] = []
    items = []

    if isinstance(data, list):
        items = data[:limit]
    elif isinstance(data, dict):
        items = data.get("products", data.get("results", data.get("items", [])))[:limit]
    if not items:
        return []

    for p in items:
        pid = str(p.get("id", p.get("productId", p.get("articleNumber", ""))))
        if not pid:
            continue
        price_data = p.get("price", {}) or p.get("priceInfo", {}) or {}
        if isinstance(price_data, (int, float)):
            price = float(price_data)
        else:
            price = float(price_data.get("current", price_data.get("value", 0)) or 0)
        title = p.get("name", p.get("title", p.get("productTitle", ""))) or "Unbekannt"
        variants = []
        sizes = p.get("variants", p.get("sizes", [])) or []
        for v in (sizes if isinstance(sizes, list) else []):
            if isinstance(v, dict):
                variants.append(ProductVariant(size=v.get("size"), color=v.get("color"), sku=v.get("sku")))
            elif isinstance(v, str):
                variants.append(ProductVariant(size=v))

        delivery = p.get("delivery", {}) or p.get("estimatedDeliveryDays")
        if isinstance(delivery, dict):
            delivery_days = delivery.get("days", delivery.get("estimatedDeliveryDays"))
        else:
            delivery_days = int(delivery) if delivery is not None else None

        products.append(RetailerProduct(
            retailer_id="asos",
            product_id=pid,
            title=title,
            price=price,
            currency="EUR",
            delivery_estimate_days=delivery_days,
            image_url=p.get("imageUrl", p.get("image", p.get("thumbnail", ""))) or None,
            product_url=p.get("url", p.get("link", "")) or None,
            variants=variants,
            raw=p,
        ))

    return products
