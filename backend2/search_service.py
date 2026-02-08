"""Suche basierend auf User-Brief (Agent-Daten) → API-Service getProductList → Ranking → SearchResultOut."""
from schemas import ShoppingSpecOut, SearchResultOut

from api_service import get_reference_data, get_product_list
from retailers.asos_api import (
    _category_to_api_id,
    _normalize_country_code,
    _parse_asos_response,
    _store_language_for_country,
)
from ranking import rank_products, why_first


def _spec_to_product_list_params(spec: ShoppingSpecOut, limit_per_retailer: int = 50) -> dict:
    """Leitet aus dem Brief (User-Antworten) die Parameter für getProductList ab."""
    country = _normalize_country_code(spec.country) if spec.country else "DE"
    store, language = _store_language_for_country(country)
    language_short = language.split("-")[0] if language else "en"
    size_schema = "US" if store == "US" else "EU"
    currency = (spec.budget_currency or "EUR").strip().upper()
    category_id = _category_to_api_id(spec.category)

    return {
        "category_id": category_id,
        "currency": currency,
        "country": country,
        "store": store,
        "language_short": language_short,
        "size_schema": size_schema,
        "limit": min(200, max(1, limit_per_retailer or 50)),
        "offset": 0,
        "sort": "recommended",
        "price_min": spec.budget_min,
        "price_max": spec.budget_max,
    }


def run_search(spec: ShoppingSpecOut, limit_per_retailer: int = 50) -> SearchResultOut:
    """
    Sucht passende Produkte basierend auf den vom Agent erfassten User-Daten (Brief).
    Lädt Referenzdaten, ruft getProductList mit brief-basierten Parametern auf,
    konvertiert zu RetailerProduct, rankt und liefert das Ergebnis für die Search-Funktion.
    """
    # Referenzdaten laden (Categories, Countries, ReturnCharges), damit Kategorie/Land gültig sind
    get_reference_data()

    params = _spec_to_product_list_params(spec, limit_per_retailer)
    raw_list = get_product_list(**params)
    # Fallback: Wenn API keine Treffer liefert, ohne category_id und Preisgrenzen erneut versuchen
    if not raw_list:
        fallback_params = {**params, "category_id": None, "price_min": None, "price_max": None}
        raw_list = get_product_list(**fallback_params)

    currency = params["currency"]
    products = _parse_asos_response(
        {"products": raw_list, "productList": raw_list},
        limit=len(raw_list),
        currency=currency,
    )

    ranked = rank_products(products, spec)
    why_first_text = why_first(ranked, spec)
    ranking_explanation = (
        "Bewertung nach: Gesamtkosten, Lieferfähigkeit bis Frist, "
        "Präferenz-Match und Set-Kohärenz. Gewichte: Kosten 35%, Lieferung 35%, Präferenz 20%, Kohärenz 10%."
    )
    return SearchResultOut(
        shopping_spec=spec,
        products=ranked,
        ranking_explanation=ranking_explanation,
        why_first=why_first_text,
    )
