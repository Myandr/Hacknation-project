"""Multi-Retailer-Suche + Ranking → SearchResultOut."""
from schemas import ShoppingSpecOut, SearchResultOut, RankedProductOut

from retailers import search_products, RetailerProduct
from ranking import rank_products, why_first


def build_search_query(spec: ShoppingSpecOut) -> str:
    """Erzeugt aus dem Brief eine Suchanfrage für die Händler."""
    parts = []
    if spec.reason:
        parts.append(spec.reason)
    if spec.event_type:
        parts.append(spec.event_type)
    if spec.preferences:
        parts.extend(spec.preferences[:3])
    if spec.must_haves:
        parts.extend(spec.must_haves[:2])
    if spec.category and spec.category != "other":
        parts.append(spec.category)
    return " ".join(parts) if parts else "outfit clothing"


def run_search(spec: ShoppingSpecOut, limit_per_retailer: int = 8) -> SearchResultOut:
    """Sucht bei allen Händlern, rankt und liefert Erklärung."""
    query = build_search_query(spec)
    category = spec.category if spec.category != "both" else "clothing"
    raw_products = search_products(query=query, category=category, limit_per_retailer=limit_per_retailer)
    ranked = rank_products([p for p in raw_products], spec)
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
