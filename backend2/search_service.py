"""Suche: Demo-Händler (StyleHub, UrbanOutfit, SportDirect) + Ranking."""
from retailers import search_products
from ranking import rank_products, why_first
from schemas import ShoppingSpecOut, SearchResultOut, RankedProductOut


def run_search(spec: ShoppingSpecOut) -> SearchResultOut:
    """
    Sucht passende Produkte basierend auf dem Brief.
    Nutzt nur Demo-Daten der Mock-Händler und bewertet sie mit dem Ranking.
    """
    currency = (spec.budget_currency or "EUR").strip().upper()
    query = " ".join(
        filter(None, [
            spec.reason,
            spec.event_type,
            spec.event_name,
            *(spec.must_haves or []),
            *(spec.nice_to_haves or []),
        ])
    ).strip() or "ski winter party"
    limit_per_retailer = 12
    products = search_products(
        query=query,
        category=spec.category,
        limit_per_retailer=limit_per_retailer,
        spec=spec,
    )
    ranked: list[RankedProductOut] = rank_products(products, spec)
    ranking_explanation = (
        "Bewertung nach: Gesamtkosten, Lieferfähigkeit bis Frist, "
        "Präferenz-Match und Set-Kohärenz. Gewichte: Kosten 35%, Lieferung 35%, Präferenz 20%, Kohärenz 10%."
    )
    why_first_text = why_first(ranked, spec) if ranked else "Keine Produkte in den Demo-Daten gefunden."
    return SearchResultOut(
        shopping_spec=spec,
        products=ranked,
        ranking_explanation=ranking_explanation,
        why_first=why_first_text,
    )
