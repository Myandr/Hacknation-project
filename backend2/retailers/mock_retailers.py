"""Drei Mock-Händler mit vielen Demo-Produktdaten (StyleHub, UrbanOutfit, SportDirect)."""
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
    RetailerProduct("stylehub", "sh-9", "Fleece-Weste Herren", 49.99, "EUR", 3, None, None, [ProductVariant(size="S"), ProductVariant(size="M"), ProductVariant(size="L")], {}),
    RetailerProduct("stylehub", "sh-10", "Ski-Brille UV400", 39.99, "EUR", 2, None, None, [], {}),
    RetailerProduct("stylehub", "sh-11", "Party-Shirt Glitzer", 27.99, "EUR", 2, None, None, [ProductVariant(size="S", color="Gold"), ProductVariant(size="M", color="Silver")], {}),
    RetailerProduct("stylehub", "sh-12", "Wintersocken Pack 3er", 14.99, "EUR", 2, None, None, [], {}),
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
    RetailerProduct("urbanoutfit", "uo-9", "Oversize Sweatshirt", 42.00, "EUR", 3, None, None, [ProductVariant(size="M"), ProductVariant(size="L")], {}),
    RetailerProduct("urbanoutfit", "uo-10", "Cargo-Hose Winter", 64.99, "EUR", 4, None, None, [ProductVariant(size="M"), ProductVariant(size="L")], {}),
    RetailerProduct("urbanoutfit", "uo-11", "Event-Parka reflektierend", 89.00, "EUR", 5, None, None, [ProductVariant(size="M", color="Black")], {}),
    RetailerProduct("urbanoutfit", "uo-12", "Basecap Team-Logo", 22.99, "EUR", 2, None, None, [], {}),
]

# SportDirect: Sport, Outdoor, Ski
SPORTDIRECT_PRODUCTS = [
    RetailerProduct("sportdirect", "sd-1", "Ski-Jacke Pro wasserdicht", 119.99, "EUR", 4, None, None, [ProductVariant(size="S"), ProductVariant(size="M"), ProductVariant(size="L")], {}),
    RetailerProduct("sportdirect", "sd-2", "Skihose mit Lüftung", 74.99, "EUR", 4, None, None, [ProductVariant(size="M"), ProductVariant(size="L")], {}),
    RetailerProduct("sportdirect", "sd-3", "Ski-Helm Gr. M/L", 59.99, "EUR", 3, None, None, [], {}),
    RetailerProduct("sportdirect", "sd-4", "Rückenprotektor Ski", 89.00, "EUR", 5, None, None, [ProductVariant(size="M"), ProductVariant(size="L")], {}),
    RetailerProduct("sportdirect", "sd-5", "Thermo-Langarm Unterwäsche", 29.99, "EUR", 2, None, None, [ProductVariant(size="S"), ProductVariant(size="M"), ProductVariant(size="L")], {}),
    RetailerProduct("sportdirect", "sd-6", "Skistiefel Warm", 149.00, "EUR", 5, None, None, [ProductVariant(size="42"), ProductVariant(size="43"), ProductVariant(size="44")], {}),
    RetailerProduct("sportdirect", "sd-7", "Skihandschuhe mit Innenfutter", 34.99, "EUR", 3, None, None, [], {}),
    RetailerProduct("sportdirect", "sd-8", "Neck Warmer Schwarz", 12.99, "EUR", 2, None, None, [], {}),
    RetailerProduct("sportdirect", "sd-9", "Softshell-Jacke Damen", 69.99, "EUR", 4, None, None, [ProductVariant(size="XS"), ProductVariant(size="S"), ProductVariant(size="M")], {}),
    RetailerProduct("sportdirect", "sd-10", "Ski-Goggles mit Wechselglas", 44.99, "EUR", 2, None, None, [], {}),
    RetailerProduct("sportdirect", "sd-11", "Team-Anorak einteilig", 94.99, "EUR", 5, None, None, [ProductVariant(size="M"), ProductVariant(size="L")], {}),
    RetailerProduct("sportdirect", "sd-12", "Wander-Stiefel wasserfest", 79.99, "EUR", 4, None, None, [ProductVariant(size="41"), ProductVariant(size="42"), ProductVariant(size="43")], {}),
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


def search_sportdirect(query: str, category: str | None = None, limit: int = 10) -> list[RetailerProduct]:
    return _filter_mock(query, SPORTDIRECT_PRODUCTS, limit)
