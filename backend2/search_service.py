"""Suche: gibt Standard-Daten basierend auf dem Brief zurück (keine API-Anbindung)."""
from schemas import ShoppingSpecOut, SearchResultOut, RankedProductOut


def run_search(spec: ShoppingSpecOut) -> SearchResultOut:
    """
    Sucht passende Produkte basierend auf dem Brief.
    Liefert Default-Daten (leere Produktliste), keine externen API-Aufrufe.
    """
    currency = (spec.budget_currency or "EUR").strip().upper()
    products: list[RankedProductOut] = []
    ranking_explanation = (
        "Bewertung nach: Gesamtkosten, Lieferfähigkeit bis Frist, "
        "Präferenz-Match und Set-Kohärenz. Gewichte: Kosten 35%, Lieferung 35%, Präferenz 20%, Kohärenz 10%."
    )
    why_first = "Keine Produkte in den Standard-Daten." if not products else ""
    return SearchResultOut(
        shopping_spec=spec,
        products=products,
        ranking_explanation=ranking_explanation,
        why_first=why_first,
    )
