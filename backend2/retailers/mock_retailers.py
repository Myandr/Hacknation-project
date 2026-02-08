"""Zwei Mock-Händler mit realistischen Produktdaten (≥3 Händler mit ASOS)."""
from schemas import ProductVariant
from retailers.base import RetailerProduct

# StyleHub: Mode, Sport, Party
STYLEHUB_PRODUCTS = [
    RetailerProduct("stylehub", "sh-1", "Herren Ski-Jacke wasserabweisend", 89.99, "EUR", 3, None, None, [ProductVariant(size="S"), ProductVariant(size="M"), ProductVariant(size="L")], {}),
    RetailerProduct("stylehub", "sh-2", "Skihose warm gefüttert", 59.99, "EUR", 4, None, None, [ProductVariant(size="M"), ProductVariant(size="L")], {}),
    RetailerProduct("stylehub", "sh-3", "Team-Logo Kapuzenpulli", 34.99, "EUR", 2, None, None, [ProductVariant(size="S", color="Navy"), ProductVariant(size="M", color="Navy")], {}),
    RetailerProduct("stylehub", "sh-4", "Wintermütze Team-Farben", 19.99, "EUR", 2, None, None, [], {}),
    RetailerProduct("stylehub", "sh-5", "Thermo-Unterwäsche Set", 44.99, "EUR", 5, None, None, [ProductVariant(size="M"), ProductVariant(size="L")], {}),
    RetailerProduct("stylehub", "sh-6", "Skihandschuhe wasserfest", 29.99, "EUR", 3, None, None, [], {}),
    RetailerProduct("stylehub", "sh-7", "Schal Stripes", 24.99, "EUR", 2, None, None, [], {}),
    RetailerProduct("stylehub", "sh-8", "Softshell-Jacke Herren", 79.99, "EUR", 4, None, None, [ProductVariant(size="M"), ProductVariant(size="L")], {}),
]

# UrbanOutfit: Streetwear, Party, Events
URBAN_PRODUCTS = [
    RetailerProduct("urbanoutfit", "uo-1", "Ski-Jacke Urban Style", 129.00, "EUR", 5, None, None, [ProductVariant(size="M", color="Black"), ProductVariant(size="L", color="Black")], {}),
    RetailerProduct("urbanoutfit", "uo-2", "Warme Winterjacke", 99.00, "EUR", 4, None, None, [ProductVariant(size="S"), ProductVariant(size="M"), ProductVariant(size="L")], {}),
    RetailerProduct("urbanoutfit", "uo-3", "Party Hoodie mit Aufdruck", 45.00, "EUR", 2, None, None, [ProductVariant(size="M", color="Grey")], {}),
    RetailerProduct("urbanoutfit", "uo-4", "Jogginghose Winter", 39.99, "EUR", 3, None, None, [ProductVariant(size="M"), ProductVariant(size="L")], {}),
    RetailerProduct("urbanoutfit", "uo-5", "Sturmhaube Ski", 18.00, "EUR", 2, None, None, [], {}),
    RetailerProduct("urbanoutfit", "uo-6", "Fleece-Pullover", 54.99, "EUR", 4, None, None, [ProductVariant(size="M")], {}),
    RetailerProduct("urbanoutfit", "uo-7", "Wasserdichte Skihose", 69.00, "EUR", 5, None, None, [ProductVariant(size="M"), ProductVariant(size="L")], {}),
    RetailerProduct("urbanoutfit", "uo-8", "Team-Trikot Langarm", 49.99, "EUR", 3, None, None, [ProductVariant(size="S", color="Red"), ProductVariant(size="M", color="Red")], {}),
]


def _filter_mock(query: str, products: list[RetailerProduct], limit: int) -> list[RetailerProduct]:
    q = (query or "").lower()
    if not q:
        return products[:limit]
    out = [p for p in products if q in p.title.lower() or q in p.retailer_id]
    return (out + products)[:limit]


def search_stylehub(query: str, category: str | None = None, limit: int = 10) -> list[RetailerProduct]:
    return _filter_mock(query, STYLEHUB_PRODUCTS, limit)


def search_urbanoutfit(query: str, category: str | None = None, limit: int = 10) -> list[RetailerProduct]:
    return _filter_mock(query, URBAN_PRODUCTS, limit)
