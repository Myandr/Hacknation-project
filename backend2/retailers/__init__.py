"""Multi-Retailer: nur Demo-Mock-Händler (StyleHub, UrbanOutfit, SportDirect)."""
from typing import Any

from .base import RetailerProduct, search_all_retailers
from .mock_retailers import search_stylehub, search_urbanoutfit, search_sportdirect

RETAILERS = [
    ("stylehub", search_stylehub, "StyleHub"),
    ("urbanoutfit", search_urbanoutfit, "UrbanOutfit"),
    ("sportdirect", search_sportdirect, "SportDirect"),
]


def search_products(
    query: str,
    category: str | None = None,
    limit_per_retailer: int = 10,
    spec: Any = None,
) -> list[RetailerProduct]:
    """Durchsucht alle Demo-Händler und gibt vereinheitlichte Produkte zurück."""
    return search_all_retailers(
        retailers=RETAILERS,
        query=query,
        category=category,
        limit_per_retailer=limit_per_retailer,
        spec=spec,
    )
