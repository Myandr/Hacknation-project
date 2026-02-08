"""
KI-gesteuerte Online-Suche mit Gemini + Google Search Grounding.

Ablauf:
1. Plan: KI entscheidet, welche Shops passen und ob es ein Outfit ist (wie viele Teile).
2. Suche: KI sucht im Web auf diesen Shops nach Produkten (Google Search).
3. Vergleich: KI wählt pro Outfit-Teil 2 beste Optionen und präsentiert sie.
"""

import json
import re
import logging
from typing import Any

from config import GOOGLE_API_KEY, GEMINI_MODEL
from schemas import (
    ShoppingSpecOut,
    OnlineSearchResultOut,
    OutfitPartOut,
    RankedProductOut,
)

logger = logging.getLogger(__name__)

# Maximale Anzahl Shops und Optionen pro Outfit-Teil
MAX_SHOPS = 5
OPTIONS_PER_PART = 2
MAX_PRODUCTS_PER_SEARCH = 8


def _spec_to_context(spec: ShoppingSpecOut) -> str:
    """Brief in lesbaren Text für Prompts umwandeln."""
    parts = []
    if spec.reason or spec.event_type:
        parts.append(f"Anlass/Grund: {spec.reason or spec.event_type}")
    if spec.category:
        parts.append(f"Kategorie: {spec.category}")
    if spec.budget_min is not None or spec.budget_max is not None:
        currency = spec.budget_currency or "EUR"
        parts.append(f"Budget: {spec.budget_min or '?'} - {spec.budget_max or '?'} {currency}")
    if spec.delivery_deadline:
        parts.append(f"Lieferung bis: {spec.delivery_deadline}")
    if spec.preferences:
        parts.append(f"Präferenzen: {', '.join(spec.preferences)}")
    if spec.must_haves:
        parts.append(f"Must-haves: {', '.join(spec.must_haves)}")
    if spec.country:
        parts.append(f"Land: {spec.country}")
    return "\n".join(parts) if parts else "Keine weiteren Angaben"


def _get_gemini_client_with_search():
    """Gemini-Client mit Google-Search-Grounding für Live-Web-Suche (Gemini 2.0+)."""
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=GOOGLE_API_KEY)
    # Google Search: KI sucht selbst im Web (Gemini 2.0+: google_search)
    grounding_tool = None
    try:
        grounding_tool = types.Tool(google_search=types.GoogleSearch())
    except (TypeError, AttributeError):
        logger.info("Google Search Tool nicht verfügbar, Suche ohne Web-Grounding.")
    config = types.GenerateContentConfig(
        tools=[grounding_tool] if grounding_tool else [],
        temperature=0.4,
    )
    return client, config


def _get_gemini_client_no_search():
    """Gemini-Client ohne Web-Suche (nur Planung/Struktur)."""
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=GOOGLE_API_KEY)
    config = types.GenerateContentConfig(temperature=0.3)
    return client, config


def plan_shops_and_outfit(spec: ShoppingSpecOut) -> dict[str, Any]:
    """
    Phase 1: KI plant Shops und bei Outfits die Teile (ohne Web-Suche).
    Gibt zurück: shops, is_outfit, outfit_parts [{ part_name, search_query }].
    """
    from google.genai import types

    if not GOOGLE_API_KEY:
        return {
            "shops": ["ASOS", "Zalando", "About You"],
            "is_outfit": spec.category == "clothing",
            "outfit_parts": [],
            "fallback": True,
        }

    context = _spec_to_context(spec)
    prompt = f"""Du bist ein Einkaufs-Assistent. Der Nutzer hat folgenden Einkaufs-Brief:

{context}

Aufgabe:
1) Nenne 3 bis {MAX_SHOPS} konkrete Online-Shops (z. B. ASOS, Zalando, About You, H&M, Zara), die für diese Suche am besten passen. Nur Shops, die es wirklich gibt und die zum Anlass passen.
2) Entscheide: Ist das ein **Outfit** (mehrere Kleidungsstücke die zusammenpassen)? Wenn ja: Definiere die einzelnen Teile (z. B. "Oberteil", "Hose", "Schuhe" oder "Jacke", "Pullover", "Jeans", "Stiefel"). Pro Teil brauchen wir später eine Suchanfrage.
3) Wenn Outfit: Gib für jedes Teil eine kurze Suchanfrage (z. B. "dunkelblaue Winterjacke Herren" oder "weiße Sneaker").

Antworte NUR mit einem gültigen JSON-Objekt, kein anderer Text davor oder danach. Format:
{{
  "shops": ["Shop1", "Shop2", ...],
  "is_outfit": true oder false,
  "outfit_parts": [
    {{ "part_name": "Oberteil", "search_query": "suchbegriffe für dieses Teil" }},
    ...
  ]
}}
Wenn is_outfit false ist, lasse outfit_parts als leeres Array [].
"""

    client, config = _get_gemini_client_no_search()
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=config,
    )
    text = (response.text or "").strip()

    # JSON aus Antwort extrahieren (falls Markdown-Codeblock)
    json_match = re.search(r"```(?:json)?\s*(\{[\s\S]*?\})\s*```", text)
    if json_match:
        text = json_match.group(1)
    else:
        # Ersten { ... } Block nehmen
        start = text.find("{")
        if start >= 0:
            depth = 0
            for i in range(start, len(text)):
                if text[i] == "{":
                    depth += 1
                elif text[i] == "}":
                    depth -= 1
                    if depth == 0:
                        text = text[start : i + 1]
                        break

    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        logger.warning("Plan-JSON konnte nicht geparst werden: %s. Fallback.", e)
        return {
            "shops": ["ASOS", "Zalando", "About You"],
            "is_outfit": spec.category == "clothing",
            "outfit_parts": [],
            "fallback": True,
        }

    shops = data.get("shops") or ["ASOS", "Zalando"]
    is_outfit = bool(data.get("is_outfit"))
    outfit_parts = data.get("outfit_parts") or []
    return {
        "shops": shops[:MAX_SHOPS],
        "is_outfit": is_outfit,
        "outfit_parts": outfit_parts,
    }


def _parse_products_from_text(block: str, retailer_id: str = "web") -> list[dict[str, Any]]:
    """
    Versucht aus einem Textblock Produkte zu extrahieren (Name, Preis, URL).
    Erwartet Zeilen wie "Titel | 49.99 EUR | https://..." oder JSON-ähnlich.
    """
    products = []
    currency_re = re.compile(r"(\d+[.,]\d{2})\s*([A-Z]{3})?")
    url_re = re.compile(r"https?://[^\s\)\]\"']+")

    for line in block.split("\n"):
        line = line.strip()
        if not line or len(line) < 10:
            continue
        urls = url_re.findall(line)
        url = urls[0] if urls else None
        prices = currency_re.findall(line)
        price_val = None
        currency = "EUR"
        if prices:
            price_val = float(prices[0][0].replace(",", "."))
            if prices[0][1]:
                currency = prices[0][1]
        # Titel: alles vor dem ersten Preis oder vor der URL
        title = line
        if url:
            title = line.split(url)[0].strip()
        if price_val is not None:
            for m in currency_re.finditer(line):
                title = line[: m.start()].strip()
                break
        title = re.sub(r"^[\d.)\-\*]\s*", "", title).strip()
        if len(title) < 3:
            continue
        products.append({
            "title": title[:200],
            "price": price_val or 0.0,
            "currency": currency,
            "product_url": url,
            "retailer_id": retailer_id,
            "product_id": url or f"web-{len(products)}",
        })
    return products


def search_products_with_web(spec: ShoppingSpecOut, plan: dict[str, Any]) -> dict[str, Any]:
    """
    Phase 2: KI sucht mit Google Search nach Produkten auf den geplanten Shops.
    Bei Outfit: eine Suche pro Teil; sonst eine allgemeine Suche.
    Liefert rohe Produkt-Listen pro Kategorie (outfit_parts) oder eine flache Liste.
    """
    from google.genai import types

    if not GOOGLE_API_KEY:
        return {"by_part": [], "products": [], "recommendation_text": "GOOGLE_API_KEY fehlt."}

    context = _spec_to_context(spec)
    shops_str = ", ".join(plan.get("shops", [])[:MAX_SHOPS])
    is_outfit = plan.get("is_outfit", False)
    outfit_parts = plan.get("outfit_parts", [])

    if is_outfit and outfit_parts:
        # Pro Outfit-Teil: eine Suchanfrage mit Grounding
        by_part = []
        all_products_flat = []
        for part in outfit_parts:
            part_name = part.get("part_name", "Teil")
            query = part.get("search_query", part_name)
            prompt = f"""Kontext Einkauf: {context}

Suche im Web nach konkreten Produkten für: **{part_name}**.
Suchbegriffe: {query}
Shops, die du bevorzugen sollst: {shops_str}

Finde {MAX_PRODUCTS_PER_SEARCH} echte, aktuell erhältliche Produkte. Pro Produkt eine Zeile im Format:
Titel des Produkts | Preis (Zahl und Währung, z.B. 49.99 EUR) | genaue URL zur Produktseite

Nur echte Treffer mit Preis und Link. Keine Einleitung, nur die Zeilen."""

            client, config = _get_gemini_client_with_search()
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
                config=config,
            )
            text = (response.text or "").strip()
            products = _parse_products_from_text(text, retailer_id="web")
            by_part.append({
                "part_name": part_name,
                "search_query": query,
                "products": products,
            })
            all_products_flat.extend(products)
        return {
            "by_part": by_part,
            "products": all_products_flat,
            "recommendation_text": "",
        }
    else:
        # Kein Outfit: eine allgemeine Suche
        reason = spec.reason or spec.event_type or "passende Produkte"
        prompt = f"""Kontext Einkauf: {context}

Suche im Web nach konkreten Produkten für: {reason}
Shops, die du bevorzugen sollst: {shops_str}

Finde {MAX_PRODUCTS_PER_SEARCH} echte, aktuell erhältliche Produkte. Pro Produkt eine Zeile:
Titel | Preis (Zahl + Währung) | URL zur Produktseite

Nur echte Treffer mit Preis und Link. Keine Einleitung."""

        client, config = _get_gemini_client_with_search()
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=config,
        )
        text = (response.text or "").strip()
        products = _parse_products_from_text(text, retailer_id="web")
        return {
            "by_part": [],
            "products": products,
            "recommendation_text": "",
        }


def compare_and_pick_best(
    spec: ShoppingSpecOut,
    plan: dict[str, Any],
    search_result: dict[str, Any],
) -> tuple[list[OutfitPartOut], list[RankedProductOut], str]:
    """
    Phase 3: KI vergleicht die gefundenen Produkte und wählt pro Outfit-Teil
    die 2 besten Optionen; bei Nicht-Outfit die besten Produkte insgesamt.
    """
    from google.genai import types

    by_part = search_result.get("by_part", [])
    products_flat = search_result.get("products", [])
    is_outfit = plan.get("is_outfit", False) and by_part

    if not GOOGLE_API_KEY:
        # Fallback: einfach erste 2 pro Teil oder erste 5 insgesamt
        if is_outfit:
            outfit_parts_out = []
            for p in by_part:
                prods = p.get("products", [])[:OPTIONS_PER_PART]
                ranked = [
                    RankedProductOut(
                        retailer_id=x.get("retailer_id", "web"),
                        product_id=x.get("product_id", ""),
                        title=x.get("title", ""),
                        price=x.get("price", 0),
                        currency=x.get("currency", "EUR"),
                        delivery_estimate_days=None,
                        image_url=None,
                        product_url=x.get("product_url"),
                        score=1.0 - i * 0.1,
                        score_breakdown={},
                        explanation="",
                    )
                    for i, x in enumerate(prods)
                ]
                outfit_parts_out.append(OutfitPartOut(part_name=p["part_name"], options=ranked))
            return outfit_parts_out, [], "Vergleich ohne KI (API-Key fehlt)."
        else:
            ranked = [
                RankedProductOut(
                    retailer_id=x.get("retailer_id", "web"),
                    product_id=x.get("product_id", ""),
                    title=x.get("title", ""),
                    price=x.get("price", 0),
                    currency=x.get("currency", "EUR"),
                    delivery_estimate_days=None,
                    image_url=None,
                    product_url=x.get("product_url"),
                    score=1.0 - i * 0.05,
                    score_breakdown={},
                    explanation="",
                )
                for i, x in enumerate(products_flat[:10])
            ]
            return [], ranked, "Liste ohne KI-Vergleich."

    context = _spec_to_context(spec)
    if is_outfit:
        # Prompt: Für jeden Teil die 2 besten aus der Liste wählen und kurz begründen
        parts_text = []
        for p in by_part:
            prods = p.get("products", [])
            lines = [f"- {x.get('title', '')} | {x.get('price')} {x.get('currency', 'EUR')} | {x.get('product_url', '')}" for x in prods]
            parts_text.append(f"**{p['part_name']}** (Suchanfrage: {p.get('search_query', '')}):\n" + "\n".join(lines[:15]))

        prompt = f"""Einkaufs-Brief: {context}

Du hast pro Outfit-Teil folgende Treffer gefunden:

{chr(10).join(parts_text)}

Wähle für JEDES Teil genau die **2 besten** Optionen (Preis, Passung zum Brief, Qualität). Antworte im JSON-Format:

{{
  "recommendation_text": "1-2 Sätze Gesamtempfehlung auf Deutsch",
  "parts": [
    {{
      "part_name": "Name des Teils",
      "chosen_indices": [0, 1]
    }}
  ]
}}

chosen_indices sind die 0-basierten Indizes in der jeweiligen Liste oben (nur 0 und 1 = die zwei gewählten). Wenn eine Liste weniger als 2 Einträge hat, nimm alle.
Antworte NUR mit diesem JSON, kein anderer Text."""

        client, config = _get_gemini_client_no_search()
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=config,
        )
        text = (response.text or "").strip()
        json_match = re.search(r"```(?:json)?\s*(\{[\s\S]*?\})\s*```", text)
        if json_match:
            text = json_match.group(1)
        start = text.find("{")
        if start >= 0:
            depth = 0
            for i in range(start, len(text)):
                if text[i] == "{":
                    depth += 1
                elif text[i] == "}":
                    depth -= 1
                    if depth == 0:
                        text = text[start : i + 1]
                        break

        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            data = {}

        recommendation_text = data.get("recommendation_text", "")
        outfit_parts_out = []
        for i, p in enumerate(by_part):
            part_name = p["part_name"]
            prods = p.get("products", [])
            chosen = [0, 1]
            for rec in data.get("parts", []):
                if rec.get("part_name") == part_name:
                    chosen = rec.get("chosen_indices", [0, 1])[:OPTIONS_PER_PART]
                    break
            options = []
            for idx in chosen:
                if 0 <= idx < len(prods):
                    x = prods[idx]
                    options.append(
                        RankedProductOut(
                            retailer_id=x.get("retailer_id", "web"),
                            product_id=x.get("product_id", ""),
                            title=x.get("title", ""),
                            price=x.get("price", 0),
                            currency=x.get("currency", "EUR"),
                            delivery_estimate_days=None,
                            image_url=None,
                            product_url=x.get("product_url"),
                            score=1.0,
                            score_breakdown={},
                            explanation="",
                        )
                    )
            outfit_parts_out.append(OutfitPartOut(part_name=part_name, options=options))
        return outfit_parts_out, [], recommendation_text
    else:
        # Nicht-Outfit: beste Produkte aus products_flat wählen und Empfehlungstext
        lines = [f"- {x.get('title', '')} | {x.get('price')} {x.get('currency', 'EUR')} | {x.get('product_url', '')}" for x in products_flat[:20]]
        prompt = f"""Einkaufs-Brief: {context}

Gefundene Produkte:
{chr(10).join(lines)}

Wähle die **5 besten** Optionen (Indizes 0 bis {len(products_flat) - 1}) und gib einen kurzen Empfehlungstext. JSON:
{{
  "recommendation_text": "1-2 Sätze auf Deutsch",
  "chosen_indices": [0, 1, 2, 3, 4]
}}

Nur dieses JSON."""

        client, config = _get_gemini_client_no_search()
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=config,
        )
        text = (response.text or "").strip()
        json_match = re.search(r"```(?:json)?\s*(\{[\s\S]*?\})\s*```", text)
        if json_match:
            text = json_match.group(1)
        start = text.find("{")
        if start >= 0:
            depth = 0
            for i in range(start, len(text)):
                if text[i] == "{":
                    depth += 1
                elif text[i] == "}":
                    depth -= 1
                    if depth == 0:
                        text = text[start : i + 1]
                        break
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            data = {}
        recommendation_text = data.get("recommendation_text", "")
        chosen = data.get("chosen_indices", list(range(min(5, len(products_flat)))))
        ranked = []
        for idx in chosen:
            if 0 <= idx < len(products_flat):
                x = products_flat[idx]
                ranked.append(
                    RankedProductOut(
                        retailer_id=x.get("retailer_id", "web"),
                        product_id=x.get("product_id", ""),
                        title=x.get("title", ""),
                        price=x.get("price", 0),
                        currency=x.get("currency", "EUR"),
                        delivery_estimate_days=None,
                        image_url=None,
                        product_url=x.get("product_url"),
                        score=1.0,
                        score_breakdown={},
                        explanation="",
                    )
                )
        return [], ranked, recommendation_text


def run_online_search(spec: ShoppingSpecOut) -> OnlineSearchResultOut:
    """
    Vollständiger Ablauf: Plan → Web-Suche → Vergleich → strukturierte Ausgabe.
    Die KI entscheidet Shops, Outfit-Teile, sucht online und präsentiert die besten Optionen.
    """
    plan = plan_shops_and_outfit(spec)
    shops = plan.get("shops", [])
    search_result = search_products_with_web(spec, plan)
    outfit_parts_out, products_ranked, recommendation_text = compare_and_pick_best(
        spec, plan, search_result
    )

    return OnlineSearchResultOut(
        shopping_spec=spec,
        is_outfit=plan.get("is_outfit", False),
        outfit_parts=outfit_parts_out,
        products=products_ranked,
        shops_considered=shops,
        recommendation_text=recommendation_text,
        search_queries_used=[p.get("search_query", "") for p in plan.get("outfit_parts", [])],
    )
