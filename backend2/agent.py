"""
Agentic Commerce – KI-Agent mit Google Gemini (google-genai).
Erfasst konversationell Budget, Lieferfrist, Präferenzen und erzeugt einen strukturierten Shopping-Brief.
"""

import json
from datetime import date

from config import GOOGLE_API_KEY, GEMINI_MODEL


def _today() -> str:
    return date.today().isoformat()


def _build_system_prompt() -> str:
    return f"""\
Du bist der Shopping-Agent für **Agentic Commerce**. Du hilfst Nutzern, einen konkreten Einkaufsauftrag zu formulieren – nicht nur Empfehlungen, sondern ein klares Briefing für den Kauf über mehrere Händler.

**Heutiges Datum: {_today()}**
Rechne relative Angaben ("bis Freitag", "in 5 Tagen") in ein Datum YYYY-MM-DD um.

---

### Szenarien (Beispiele)
- **Super-Bowl-Party-Outfit:** Volles Outfit (Kopf bis Fuß) im Team-Style, Budget, Lieferung bis Datum.
- **Ski-Outfit:** Skikleidung, warm und wasserfest, Größe, Budget, Lieferung.
- **Hackathon-Host-Kit:** Snacks, Badges, Adapter, Deko, Preise für ~60 Personen, beste Preise.

---

### Was du sammeln sollst (strukturierter Brief)

| Feld | Pflicht? | Beschreibung |
|------|----------|--------------|
| **reason / event_type** | JA | Wofür? (party, ski, hackathon, outfit, …) – für die Produktsuche! |
| **category** | JA | Immer: `clothing`, `food`, `both` oder `other` |
| **Budget** | empfohlen | budget_min, budget_max, budget_currency (z. B. EUR) |
| **Lieferfrist** | empfohlen | Konkretes Datum YYYY-MM-DD |
| **Präferenzen** | optional | Stil, Marken, Farben, Größen (z. B. "Größe M", "wasserfest") |
| **must_haves** | optional | Was unbedingt dabei sein muss |
| **nice_to_haves** | optional | Nice-to-have |
| **people_count** | optional | Für wie viele Personen (z. B. Hackathon 60) |

---

### Verhalten
- Extrahiere aus jeder Nachricht alles Relevante und rufe **update_shopping_requirements** auf.
- Wenn 3 oder mehr der Parameter ausgefüllt sind, abschließen.
- **Maximal 2 Nachfragen**, dann abschließen – auch wenn nicht alles ausgefüllt ist. Die Nachfrage höchstens 40 Zeichen lang. kurz und knapp. Nicht nach der Kategorie fragen.
- Wenn der Nutzer schon viel sagt (z. B. "Ski-Outfit, 400€, Größe M, in 5 Tagen"), direkt abschließen.
- Zum Abschließen: **update_shopping_requirements** (letzte Werte) + **mark_requirements_complete** aufrufen.
- Antworte in der Sprache des Nutzers.
- Wenn keine Frage gestellt wird im output, abschließen!
- Tätige keinen Aussagen! Stelle nur Fragen.
"""


_REQUIREMENTS_PROPERTIES = {
    "budget_min": {"type": "number", "description": "Minimales Budget"},
    "budget_max": {"type": "number", "description": "Maximales Budget"},
    "budget_currency": {"type": "string", "description": "Währung (EUR, USD, GBP)"},
    "delivery_deadline": {"type": "string", "description": "Lieferfrist als Datum YYYY-MM-DD"},
    "category": {
        "type": "string",
        "enum": ["clothing", "food", "both", "other"],
        "description": "Kategorie: clothing, food, both, other",
    },
    "event_type": {"type": "string", "description": "Art des Anlasses"},
    "event_name": {"type": "string", "description": "Name/Beschreibung des Events"},
    "people_count": {"type": "integer", "description": "Anzahl Personen"},
    "reason": {"type": "string", "description": "Grund für den Einkauf (z. B. ski, party)"},
    "preferences": {"type": "array", "items": {"type": "string"}, "description": "Stil, Größe, Farbe, Marke"},
    "must_haves": {"type": "array", "items": {"type": "string"}, "description": "Pflicht-Items"},
    "nice_to_haves": {"type": "array", "items": {"type": "string"}, "description": "Optionale Wünsche"},
}


def _build_gemini_config():
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=GOOGLE_API_KEY)
    tools = types.Tool(
        function_declarations=[
            {
                "name": "update_shopping_requirements",
                "description": "Shopping-Anforderungen aus der Nutzerantwort aktualisieren. Nur genannte/ableitbare Felder angeben.",
                "parameters": {"type": "object", "properties": _REQUIREMENTS_PROPERTIES},
            },
            {
                "name": "mark_requirements_complete",
                "description": "Brief als vollständig markieren. Aufrufen wenn genug Infos da sind oder Nutzer keine weiteren Angaben macht.",
                "parameters": {"type": "object", "properties": {}},
            },
        ]
    )
    config = types.GenerateContentConfig(
        system_instruction=_build_system_prompt(),
        tools=[tools],
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
        temperature=0.7,
    )
    return client, config


def _build_contents(conversation: list[dict], current_requirements: dict | None) -> list:
    from google.genai import types

    contents = []
    for msg in conversation:
        role = "model" if msg["role"] == "assistant" else "user"
        text = msg["content"]
        if not contents and role == "user" and current_requirements:
            text = (
                "Aktueller Brief:\n"
                + json.dumps(current_requirements, indent=2, ensure_ascii=False)
                + "\n\n---\nNächste Nutzernachricht:\n"
                + text
            )
        contents.append(types.Content(role=role, parts=[types.Part(text=text)]))
    return contents


def _parse_gemini_response(response) -> tuple[list[str], list[dict]]:
    tool_calls = []
    text_parts = []
    if not response.candidates or not response.candidates[0].content:
        return text_parts, tool_calls
    for part in response.candidates[0].content.parts:
        if part.function_call and part.function_call.name:
            fc = part.function_call
            args = dict(fc.args) if fc.args else {}
            for k, v in args.items():
                if hasattr(v, "__iter__") and not isinstance(v, str):
                    args[k] = list(v)
            tool_calls.append({"name": fc.name, "arguments": args})
        elif part.text:
            text_parts.append(part.text)
    return text_parts, tool_calls


def process_message(
    conversation_history: list[dict],
    current_requirements: dict | None,
) -> tuple[str, list[dict]]:
    """Verarbeitet eine Nutzernachricht mit Gemini; gibt (Antworttext, Tool-Calls) zurück."""
    from google.genai import types

    if not GOOGLE_API_KEY:
        return (
            "Bitte GOOGLE_API_KEY in .env setzen (Google AI Studio / Gemini).",
            [],
        )

    client, config = _build_gemini_config()
    contents = _build_contents(conversation_history, current_requirements)
    if not contents:
        return "Bitte sende eine Nachricht.", []

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=contents,
        config=config,
    )
    text_parts, tool_calls_data = _parse_gemini_response(response)

    if tool_calls_data and not text_parts:
        contents.append(response.candidates[0].content)
        fn_parts = [
            types.Part.from_function_response(name=tc["name"], response={"result": {"status": "ok"}})
            for tc in tool_calls_data
        ]
        contents.append(types.Content(role="user", parts=fn_parts))
        follow = client.models.generate_content(model=GEMINI_MODEL, contents=contents, config=config)
        if follow.candidates and follow.candidates[0].content and getattr(follow.candidates[0].content, "parts", None):
            for part in follow.candidates[0].content.parts:
                if part.text:
                    text_parts.append(part.text)
        if not text_parts:
            text_parts.append("Alles klar, ich habe deine Angaben gespeichert.")

    return "\n".join(text_parts) if text_parts else "", tool_calls_data
