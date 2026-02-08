"""Ranking-Engine: transparente Bewertung (Kosten, Lieferung, Präferenz, Kohärenz)."""
from datetime import date, timedelta

from schemas import RankedProductOut, ShoppingSpecOut
from retailers.base import RetailerProduct


def _parse_deadline(deadline: str | None) -> date | None:
    if not deadline:
        return None
    try:
        return date.fromisoformat(deadline)
    except (ValueError, TypeError):
        return None


def _delivery_feasibility_score(product: RetailerProduct, deadline: date | None) -> float:
    """1.0 = lieferbar bis Deadline, 0.0 = zu spät oder unbekannt."""
    if not deadline or product.delivery_estimate_days is None:
        return 0.5  # neutral
    delivery_date = date.today() + timedelta(days=product.delivery_estimate_days)
    if delivery_date <= deadline:
        return 1.0
    # Je später, desto schlechter
    days_late = (delivery_date - deadline).days
    return max(0.0, 1.0 - days_late / 14.0)


def _cost_score(product: RetailerProduct, budget_max: float | None) -> float:
    """1.0 = gut im Budget, 0.0 = deutlich drüber."""
    if budget_max is None or budget_max <= 0:
        return 1.0
    if product.price <= budget_max:
        return 1.0
    ratio = budget_max / product.price
    return max(0.0, ratio)


def _preference_match_score(product: RetailerProduct, spec: ShoppingSpecOut) -> float:
    """Einfache Text-Übereinstimmung mit preferences/must_haves."""
    keywords = [p.lower() for p in (spec.preferences or []) + (spec.must_haves or [])]
    if not keywords:
        return 0.5
    title = product.title.lower()
    hits = sum(1 for k in keywords if k in title)
    return min(1.0, 0.5 + 0.5 * (hits / len(keywords)))


def _set_coherence_score(products: list[RetailerProduct], index: int, spec: ShoppingSpecOut) -> float:
    """Kohärenz: gleicher Stil/Kategorie (vereinfacht: gleicher Retailer oder ähnlicher Preisbereich)."""
    if len(products) <= 1:
        return 1.0
    # Vereinfacht: mittlere Abweichung vom mittleren Preis
    prices = [p.price for p in products]
    avg = sum(prices) / len(prices)
    p = products[index].price
    deviation = abs(p - avg) / avg if avg else 0
    return max(0.0, 1.0 - deviation)


def rank_products(
    products: list[RetailerProduct],
    spec: ShoppingSpecOut,
    weights: dict[str, float] | None = None,
) -> list[RankedProductOut]:
    """Berechnet für jedes Produkt einen Score und sortiert absteigend."""
    if not products:
        return []

    w = weights or {
        "cost": 0.35,
        "delivery": 0.35,
        "preference": 0.2,
        "coherence": 0.1,
    }
    deadline = _parse_deadline(spec.delivery_deadline)
    budget_max = spec.budget_max

    ranked: list[RankedProductOut] = []
    for i, p in enumerate(products):
        cost_s = _cost_score(p, budget_max)
        del_s = _delivery_feasibility_score(p, deadline)
        pref_s = _preference_match_score(p, spec)
        coh_s = _set_coherence_score(products, i, spec)

        score = (
            w["cost"] * cost_s
            + w["delivery"] * del_s
            + w["preference"] * pref_s
            + w["coherence"] * coh_s
        )
        breakdown = {"cost": cost_s, "delivery": del_s, "preference": pref_s, "coherence": coh_s}
        explanation = (
            f"Preis: {'im Budget' if cost_s >= 0.9 else 'über Budget'}, "
            f"Lieferung: {p.delivery_estimate_days or '?'} Tage, "
            f"Präferenz-Match: {pref_s:.0%}."
        )
        po = p.to_product_out()
        ranked.append(RankedProductOut(
            **po.model_dump(),
            score=round(score, 4),
            score_breakdown=breakdown,
            explanation=explanation,
        ))

    ranked.sort(key=lambda x: x.score, reverse=True)
    return ranked


def why_first(ranked: list[RankedProductOut], spec: ShoppingSpecOut) -> str:
    """Erklärt, warum Option #1 auf Platz 1 steht."""
    if not ranked:
        return "Keine Produkte zum Bewerten."
    first = ranked[0]
    parts = [
        f"Platz 1: {first.title} ({first.retailer_id}, {first.price} {first.currency}).",
        f"Score: {first.score:.2f} (Kosten: {first.score_breakdown.get('cost', 0):.2f}, "
        f"Lieferung: {first.score_breakdown.get('delivery', 0):.2f}, "
        f"Präferenz: {first.score_breakdown.get('preference', 0):.2f}).",
        first.explanation,
    ]
    return " ".join(parts)
