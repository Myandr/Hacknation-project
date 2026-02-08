"""Plan aus Session-Anforderungen + Google-Shopping-Suche pro Komponente."""

from shopping_planner import run_shopping_plan


def plan_and_search(requirements: dict, location: str = "Germany") -> list[dict] | None:
    """
    Erzeugt den KI-Plan und führt pro Komponente eine Google-Shopping-Suche (q=Name) aus.
    Rückgabe: Liste von {"component": {...}, "shopping_results": [...]} für PlanComponentSearchOut.
    """
    plan = run_shopping_plan(requirements)
    if not plan or not isinstance(plan.get("components"), list):
        return None
    out = []
    for c in plan["components"]:
        # Komponente ohne shopping_results (Schema erwartet nur Plan-Komponentenfelder)
        component_dict = {k: v for k, v in c.items() if k != "shopping_results"}
        out.append({
            "component": component_dict,
            "shopping_results": c.get("shopping_results", []),
        })
    return out
