"""
API-Service für ASOS: Referenzdaten einmal laden, dann getProductList/getProductDetails
mit von der KI ausgefüllten Parametern (nur Werte aus den Referenzdaten).
"""

import logging
from typing import Any

from retailers.asos_api import (
    get_categories,
    get_countries,
    get_return_charges,
    get_product_list as asos_get_product_list,
    get_product_detail as asos_get_product_detail,
)

logger = logging.getLogger(__name__)

# Temporärer Cache der Referenzdaten (Categories, Countries, ReturnCharges)
_reference_data: dict[str, Any] | None = None


def clear_reference_data_cache() -> None:
    """Referenzdaten-Cache leeren (z. B. nach Reload für neue Kategorien-Logik)."""
    global _reference_data
    _reference_data = None


def load_reference_data() -> dict[str, Any]:
    """
    Lädt am Anfang alle Referenzdaten von der API und speichert sie temporär.
    - getCategories
    - getCountries
    - getReturnCharges
    Danach können get_product_list und get_product_details mit Werten aus diesen Daten genutzt werden.
    """
    global _reference_data
    categories = get_categories()
    countries = get_countries()
    return_charges = get_return_charges()
    _reference_data = {
        "categories": categories,
        "countries": countries,
        "return_charges": return_charges,
    }
    logger.info(
        "API-Service: Referenzdaten geladen – %d Kategorien, %d Länder",
        len(categories),
        len(countries),
    )
    return _reference_data


def get_reference_data() -> dict[str, Any]:
    """
    Gibt die zwischengespeicherten Referenzdaten zurück.
    Lädt sie bei Bedarf (beim ersten Aufruf).
    """
    global _reference_data
    if _reference_data is None:
        load_reference_data()
    return _reference_data or {
        "categories": [],
        "countries": [],
        "return_charges": None,
    }


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
    Ruft getProductList auf. Alle Parameter sollen von der KI passend gesetzt werden,
    unter Verwendung der Referenzdaten (get_reference_data()):
    - categoryId: aus categories (KI wählt passende Kategorie zum User-Request)
    - currency, country, store, languageShort, sizeSchema: aus countries/Referenz
    - limit, offset, sort, priceMin, priceMax: von KI gesetzt
    """
    return asos_get_product_list(
        category_id=category_id,
        currency=currency,
        country=country,
        store=store,
        language_short=language_short,
        size_schema=size_schema,
        limit=limit,
        offset=offset,
        sort=sort,
        price_min=price_min,
        price_max=price_max,
    )


def get_product_details(
    product_id: str,
    *,
    currency: str = "USD",
    store: str = "US",
    language: str = "en-US",
    size_schema: str = "US",
) -> dict | None:
    """
    Ruft getProductDetails für eine productId aus der getProductList-Response auf.
    Nur productId kommt aus getProductList; currency, store, language, sizeSchema
    können aus dem gleichen Kontext (Land/Store) wie bei getProductList gesetzt werden.
    """
    return asos_get_product_detail(
        product_id=product_id,
        currency=currency,
        store=store,
        language=language,
        country_code=None,
    )
