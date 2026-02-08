"""Multi-Retailer: ASOS (RapidAPI) + Mock-Händler."""
from typing import Any

from .base import RetailerProduct, search_all_retailers
from .asos_api import search_asos
from .mock_retailers import search_stylehub, search_urbanoutfit

RETAILERS = [
    ("asos", search_asos, "ASOS"),
    ("stylehub", search_stylehub, "StyleHub"),
    ("urbanoutfit", search_urbanoutfit, "UrbanOutfit"),
]


def search_products(
    query: str,
    category: str | None = None,
    limit_per_retailer: int = 10,
    spec: Any = None,
) -> list[RetailerProduct]:
    """Durchsucht alle Händler und gibt vereinheitlichte Produkte zurück. spec = KI-Brief (country/currency für ASOS)."""
    return search_all_retailers(
        retailers=RETAILERS,
        query=query,
        category=category,
        limit_per_retailer=limit_per_retailer,
        spec=spec,
    )
