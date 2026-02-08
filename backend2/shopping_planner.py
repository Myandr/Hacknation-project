"""
KI-Denkprozess: Aus Session-Daten (Brief) eine strukturierte Einkaufsliste mit Budgetaufteilung erzeugen.
Ausgabe ausschließlich als JSON – keine Fließtexte.
"""

import json
import re
from serpapi import GoogleSearch

from config import GOOGLE_API_KEY, GEMINI_MODEL, SERPAPI_KEY


def _build_plan_prompt(requirements: dict) -> str:
    return f"""Analysiere den folgenden Shopping-Brief und erzeuge eine Einkaufsliste mit sinnvoller Budgetaufteilung.

**Eingabe (Brief):**
{json.dumps(requirements, indent=2, ensure_ascii=False)}

**Regeln:**
1. Leite aus event_type, reason, must_haves, nice_to_haves und people_count alle nötigen Bestandteile/Positionen ab.
2. Teile das Gesamtbudget (budget_min/budget_max) sinnvoll auf die Positionen auf. Wenn kein Budget angegeben ist, nutze plausible Schätzungen und setze "estimated": true.
3. Antworte NUR mit einem einzigen gültigen JSON-Objekt, kein Text davor oder danach, keine Erklärungen in Prosa.
4. Schema des JSON-Objekts (exakt einhalten):

{{
  "currency": "EUR",
  "total_budget_min": number,
  "total_budget_max": number,
  "components": [
    {{
      "id": "1",
      "name": "string",
      "category": "string",
      "budget_min": number,
      "budget_max": number,
      "priority": "must_have" | "nice_to_have",
      "quantity": 1,
      "notes": []
    }}
  ]
}}

- "name": kurze Bezeichnung der Position (z.B. "Skijacke", "Snacks für 60 Personen").
- "category": z.B. "clothing", "food", "accessories", "other".
- "priority": "must_have" wenn aus must_haves/Anlass zwingend, sonst "nice_to_have".
- "quantity": Stückzahl/Personenanzahl wo sinnvoll.
- "notes": optionales Array mit kurzen Stichworten (z.B. ["Schwarz", "Größe M", "wasserfest"]). Bei Kleidung immer Farbe und Größe angeben, falls aus dem Brief ableitbar.

Antworte ausschließlich mit dem JSON-Objekt."""


def _extract_json_from_response(text: str) -> dict | None:
    """Versucht, aus der Modell-Antwort ein JSON-Objekt zu extrahieren (ggf. aus Markdown-Codeblock)."""
    text = text.strip()
    # Codeblock ```json ... ``` entfernen
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if match:
        text = match.group(1).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # Versuch: erstes { bis letztes }
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(text[start : end + 1])
        except json.JSONDecodeError:
            pass
    return None


def _build_google_search_query(component: dict, currency: str = "EUR") -> str:
    """Baut eine Suchanfrage für Google Shopping: Name, Stichworte (Farbe, Größe, …), Preisbereich.
    Beispiel: 'Skijacke, Schwarz, Größe M, 200€ bis 400€'."""
    parts = [component.get("name", "").strip()]
    notes = component.get("notes") or []
    if notes:
        parts.append(", ".join(str(n).strip() for n in notes if str(n).strip()))
    b_min = component.get("budget_min")
    b_max = component.get("budget_max")
    if b_min is not None or b_max is not None:
        curr = (currency or "EUR").strip().upper()
        sym = "€" if curr == "EUR" else curr + " "
        if b_min is not None and b_max is not None:
            parts.append(f"{b_min:.0f}{sym} bis {b_max:.0f}{sym}".replace("  ", " "))
        elif b_min is not None:
            parts.append(f"ab {b_min:.0f}{sym}")
        else:
            parts.append(f"bis {b_max:.0f}{sym}")
    return ", ".join(p for p in parts if p)


def search_google_shopping(query: str, location: str = "Germany") -> list[dict]:
    params = {
        "engine": "google_shopping",
        "q": query,
        "location": location,
        "api_key": SERPAPI_KEY,
    }
    results = GoogleSearch(params).get_dict()
    return results.get("shopping_results", [])

def run_shopping_plan(requirements: dict) -> dict | None:
    """
    Nimmt die gesammelten Session-Anforderungen (Brief) und erzeugt per KI einen
    strukturierten Einkaufsplan mit Budgetaufteilung. Rückgabe nur JSON-Daten.
    """
    if not GOOGLE_API_KEY:
        return None

    from google import genai
    from google.genai import types

    client = genai.Client(api_key=GOOGLE_API_KEY)
    prompt = _build_plan_prompt(requirements)

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.3,
            response_mime_type="application/json",
        ),
    )

    if not response.candidates or not response.candidates[0].content:
        return None

    text = ""
    for part in response.candidates[0].content.parts:
        if part.text:
            text += part.text

    if not text:
        return None

    # Bei response_mime_type="application/json" ist die Antwort oft direkt JSON
    plan = _extract_json_from_response(text)
    if plan is None:
        try:
            plan = json.loads(text)
        except json.JSONDecodeError:
            return None

    # Validierung: components vorhanden, Liste
    if not isinstance(plan.get("components"), list):
        plan["components"] = []
    if "currency" not in plan and requirements.get("budget_currency"):
        plan["currency"] = requirements["budget_currency"] or "EUR"
    if "currency" not in plan:
        plan["currency"] = "EUR"


    currency = plan.get("currency", "EUR")
    for component in plan["components"]:
        query = _build_google_search_query(component, currency)
        results = search_google_shopping(query, location="Germany")
        component["shopping_results"] = results[:3]

    return plan







