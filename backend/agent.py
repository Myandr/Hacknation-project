"""
AI-Agent – steuert die Konversation mit dem Nutzer und extrahiert
strukturierte Shopping-Anforderungen via Function Calling.

Unterstützt **OpenAI** und **Google Gemini** (google-genai SDK) –
umschaltbar per AI_PROVIDER in der .env Datei.
"""

import json
import os
from collections.abc import Generator
from datetime import date

from dotenv import load_dotenv

load_dotenv()

AI_PROVIDER: str = os.getenv("AI_PROVIDER", "gemini").lower()


def _today() -> str:
    return date.today().isoformat()


# ---------------------------------------------------------------------------
# System-Prompt  (für beide Provider gleich)
# ---------------------------------------------------------------------------
def _build_system_prompt() -> str:
    return f"""\
Du bist *ShopBuddy* – der freundliche, hilfsbereite Shopping-Assistent der Hacknation-App.
Du hilfst Nutzern, alles für ihren Anlass zusammenzustellen – egal ob Kleidung, Essen oder beides.

**Heutiges Datum: {_today()}**
Nutze dieses Datum, um relative Zeitangaben (z. B. "in zwei Wochen", "nächsten Samstag") in ein konkretes Datum im Format YYYY-MM-DD umzurechnen.

---

### Was du sammeln sollst:

| Feld | Pflicht? | Beschreibung |
|------|----------|-------------|
| **Anlass / Grund** | JA | Wofür wird eingekauft? (Hochzeit, Geburtstag, Urlaub, Business …) |
| **Kategorie** | JA | Was wird gebraucht: `clothing`, `food`, `both` oder `other`? Es kann auch etwas spezifiesches sein, wenn man zum beispiel nach einer Kategorie in Kleidung sucht (Ski, Sport, Anzüge..) Leite es aus dem Kontext ab. |
| **Location** | Automatisch | Land/Stadt werden automatisch erkannt. Du musst NICHT danach fragen. |
| **Must-Haves** | Einmal nachfragen | Frage einmal freundlich, ob es etwas gibt, das auf jeden Fall dabei sein muss. |
| Budget | optional | Min/Max + Währung (Default: EUR) |
| Lieferfrist | optional | Konkretes Datum (YYYY-MM-DD) |
| Präferenzen | optional | Stil, Marken, Farben, Größen … |
| Nice-to-Haves | optional | Wäre schön, kein Muss |
| Personenanzahl | optional | Für wie viele Leute? |
| Event-Name | optional | Name / Beschreibung |

---

### Dein Verhalten:

- Sage nichts außer der Frage, die du stellst.
- Extrahiere aus jeder Nachricht alles, was du kannst, und rufe **`update_shopping_requirements`** auf.
- **Reihenfolge der Fragen (unbedingt einhalten):**
  1. **Zuerst:** Budget (und ggf. Lieferfrist) – z. B. "Was ist dein Budget?" / "Bis wann brauchst du es?"
  2. **Dann:** Präferenzen – Stil, Marken, Farben, Größen, sonstige Wünsche
  3. **Zum Schluss:** Must-Haves – was auf jeden Fall dabei sein muss
- Stelle pro Antwort **1–2 gezielte Fragen** zu noch fehlenden Infos, immer in dieser Reihenfolge.
- **Maximal 3 Nachfragen** insgesamt (also max. 3 Antworten von dir, bevor du abschließt). Danach abschließen – auch wenn noch Felder offen sind.
- Wenn der Nutzer auf eine Frage antwortet, speichere die neuen Infos via `update_shopping_requirements` und stelle die nächste Frage – oder schließe ab, wenn genug da ist oder 3 Nachfragen erreicht sind.
- Wenn der Nutzer schon in der **ersten Nachricht** sehr viele Infos gibt (Anlass + Budget + Wünsche), darfst du auch mit weniger Nachfragen abschließen.
- Wenn der Nutzer sagt "passt so" / "keine weiteren Wünsche" o. ä., sofort abschließen.
- Zum Abschließen: `update_shopping_requirements` (letzte Infos) + **`mark_requirements_complete`** aufrufen.
- **Kategorie** (`category`): Leite aus dem Kontext ab, ob Kleidung, Essen oder beides gebraucht wird. Im Zweifelsfall: `both`.
- **Location** (country/city): Wird automatisch erkannt. Du musst NICHT danach fragen. Nutze die Info, wenn du lokale Shops oder Lieferzeiten erwähnst.
- Fehlende optionale Felder: leer lassen oder sinnvollen Default (z. B. `budget_currency` = "EUR").
- **Lieferfrist**: Wandle relative Angaben ("in 2 Wochen") immer in ein konkretes Datum um (YYYY-MM-DD).

Antworte immer in der Sprache des Nutzers.
"""


# ---------------------------------------------------------------------------
# Gemeinsame Tool-/Funktions-Parameter (Provider-unabhängig)
# ---------------------------------------------------------------------------
_REQUIREMENTS_PROPERTIES = {
    "budget_min": {
        "type": "number",
        "description": "Minimales Budget",
    },
    "budget_max": {
        "type": "number",
        "description": "Maximales Budget",
    },
    "budget_currency": {
        "type": "string",
        "description": "Währung (EUR, USD, GBP …)",
    },
    "delivery_deadline": {
        "type": "string",
        "description": "Lieferfrist als konkretes Datum YYYY-MM-DD. Relative Angaben anhand des heutigen Datums umrechnen.",
    },
    "category": {
        "type": "string",
        "enum": ["clothing", "food", "both", "other"],
        "description": "Was wird gebraucht: clothing (Kleidung), food (Essen), both (beides), other (sonstiges).",
    },
    "event_type": {
        "type": "string",
        "description": "Art des Anlasses: event, personal, gift, business, vacation, wedding, birthday, party …",
    },
    "event_name": {
        "type": "string",
        "description": "Name / Beschreibung des Events",
    },
    "people_count": {
        "type": "integer",
        "description": "Anzahl Personen, für die eingekauft wird",
    },
    "reason": {
        "type": "string",
        "description": "Genereller Grund für den Einkauf",
    },
    "preferences": {
        "type": "array",
        "items": {"type": "string"},
        "description": "Stilpräferenzen, Marken, Farben, Größen …",
    },
    "must_haves": {
        "type": "array",
        "items": {"type": "string"},
        "description": "Pflicht-Items / -Features",
    },
    "nice_to_haves": {
        "type": "array",
        "items": {"type": "string"},
        "description": "Optionale Wünsche",
    },
}

_UPDATE_DESCRIPTION = (
    "Aktualisiert die Shopping-Anforderungen mit Infos aus der "
    "Nutzernachricht.  Nur Felder angeben, die der Nutzer explizit "
    "genannt hat oder die klar ableitbar sind."
)

_COMPLETE_DESCRIPTION = (
    "Markiert die Anforderungen als vollständig.  Nur aufrufen, "
    "wenn genug Infos vorliegen oder der Nutzer keine weiteren Angaben machen möchte."
)


# ═══════════════════════════════════════════════════════════════════════════
# OpenAI  Provider
# ═══════════════════════════════════════════════════════════════════════════

def _get_openai_client():
    from openai import OpenAI
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def _openai_tools():
    return [
        {
            "type": "function",
            "function": {
                "name": "update_shopping_requirements",
                "description": _UPDATE_DESCRIPTION,
                "parameters": {
                    "type": "object",
                    "properties": _REQUIREMENTS_PROPERTIES,
                    "required": [],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "mark_requirements_complete",
                "description": _COMPLETE_DESCRIPTION,
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
        },
    ]


def _build_openai_messages(
    conversation_history: list[dict],
    current_requirements: dict | None,
) -> list[dict]:
    messages: list[dict] = [{"role": "system", "content": _build_system_prompt()}]
    if current_requirements:
        state = (
            "Aktueller Stand der gesammelten Anforderungen:\n"
            + json.dumps(current_requirements, indent=2, ensure_ascii=False)
        )
        messages.append({"role": "system", "content": state})
    for msg in conversation_history:
        messages.append({"role": msg["role"], "content": msg["content"]})
    return messages


def _process_openai(
    conversation_history: list[dict],
    current_requirements: dict | None,
) -> tuple[str, list[dict]]:
    client = _get_openai_client()
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    tools = _openai_tools()
    messages = _build_openai_messages(conversation_history, current_requirements)

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        tools=tools,
        tool_choice="auto",
        temperature=0.7,
    )

    assistant_msg = response.choices[0].message
    tool_calls_data: list[dict] = []

    if assistant_msg.tool_calls:
        for tc in assistant_msg.tool_calls:
            fn_args = json.loads(tc.function.arguments) if tc.function.arguments else {}
            tool_calls_data.append({"name": tc.function.name, "arguments": fn_args})

        messages.append(assistant_msg)  # type: ignore[arg-type]
        for tc in assistant_msg.tool_calls:
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": json.dumps({"status": "ok"}),
                }
            )

        follow_up = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice="none",
            temperature=0.7,
        )
        assistant_text = follow_up.choices[0].message.content or ""
    else:
        assistant_text = assistant_msg.content or ""

    return assistant_text, tool_calls_data


def _stream_openai(
    conversation_history: list[dict],
    current_requirements: dict | None,
) -> Generator[str, None, tuple[str, list[dict]]]:
    """OpenAI streaming: yields text chunks, returns (full_text, tool_calls)."""
    client = _get_openai_client()
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    tools = _openai_tools()
    messages = _build_openai_messages(conversation_history, current_requirements)

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        tools=tools,
        tool_choice="auto",
        temperature=0.7,
    )

    assistant_msg = response.choices[0].message
    tool_calls_data: list[dict] = []

    if assistant_msg.tool_calls:
        for tc in assistant_msg.tool_calls:
            fn_args = json.loads(tc.function.arguments) if tc.function.arguments else {}
            tool_calls_data.append({"name": tc.function.name, "arguments": fn_args})

        messages.append(assistant_msg)  # type: ignore[arg-type]
        for tc in assistant_msg.tool_calls:
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": json.dumps({"status": "ok"}),
                }
            )

        # Stream the follow-up
        stream = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice="none",
            temperature=0.7,
            stream=True,
        )
        full_text = ""
        for chunk in stream:
            delta = chunk.choices[0].delta
            if delta and delta.content:
                full_text += delta.content
                yield delta.content
        return full_text, tool_calls_data
    else:
        # Stream first call
        stream = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice="auto",
            temperature=0.7,
            stream=True,
        )
        full_text = ""
        for chunk in stream:
            delta = chunk.choices[0].delta
            if delta and delta.content:
                full_text += delta.content
                yield delta.content
        return full_text, []


# ═══════════════════════════════════════════════════════════════════════════
# Google Gemini  Provider  (google-genai SDK)
# ═══════════════════════════════════════════════════════════════════════════

def _build_gemini_config():
    """Erstellt Client, Tool-Definitionen und GenerateContentConfig."""
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    tools = types.Tool(
        function_declarations=[
            {
                "name": "update_shopping_requirements",
                "description": _UPDATE_DESCRIPTION,
                "parameters": {
                    "type": "object",
                    "properties": _REQUIREMENTS_PROPERTIES,
                },
            },
            {
                "name": "mark_requirements_complete",
                "description": _COMPLETE_DESCRIPTION,
                "parameters": {
                    "type": "object",
                    "properties": {},
                },
            },
        ]
    )

    config = types.GenerateContentConfig(
        system_instruction=_build_system_prompt(),
        tools=[tools],
        automatic_function_calling=types.AutomaticFunctionCallingConfig(
            disable=True,
        ),
        temperature=0.7,
    )

    return client, config


def _build_gemini_contents(
    conversation_history: list[dict],
    current_requirements: dict | None,
) -> list:
    """Baut die Gemini-Contents-Liste auf."""
    from google.genai import types

    contents: list[types.Content] = []

    for msg in conversation_history:
        role = "model" if msg["role"] == "assistant" else "user"
        text = msg["content"]

        if not contents and role == "user" and current_requirements:
            context = (
                "Aktueller Stand der gesammelten Anforderungen:\n"
                + json.dumps(current_requirements, indent=2, ensure_ascii=False)
                + "\n\n---\nNeue Nutzernachricht:\n"
            )
            text = context + text

        contents.append(
            types.Content(role=role, parts=[types.Part(text=text)])
        )

    return contents


def _parse_gemini_response(response) -> tuple[list[str], list[dict]]:
    """Parst eine Gemini-Response in Text-Parts und Tool-Calls."""
    tool_calls_data: list[dict] = []
    text_parts: list[str] = []

    for part in response.candidates[0].content.parts:
        if part.function_call and part.function_call.name:
            fc = part.function_call
            fn_args = dict(fc.args) if fc.args else {}
            for key, val in fn_args.items():
                if hasattr(val, "__iter__") and not isinstance(val, str):
                    fn_args[key] = list(val)
            tool_calls_data.append({"name": fc.name, "arguments": fn_args})
        elif part.text:
            text_parts.append(part.text)

    return text_parts, tool_calls_data


def _process_gemini(
    conversation_history: list[dict],
    current_requirements: dict | None,
) -> tuple[str, list[dict]]:
    from google.genai import types

    client, config = _build_gemini_config()
    model_name = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    contents = _build_gemini_contents(conversation_history, current_requirements)

    if not contents:
        return "Bitte sende eine Nachricht.", []

    response = client.models.generate_content(
        model=model_name,
        contents=contents,
        config=config,
    )

    text_parts, tool_calls_data = _parse_gemini_response(response)

    # Wenn Function Calls aber kein Text → Ergebnis zurücksenden
    if tool_calls_data and not text_parts:
        contents.append(response.candidates[0].content)

        fn_response_parts = [
            types.Part.from_function_response(
                name=tc["name"],
                response={"result": {"status": "ok"}},
            )
            for tc in tool_calls_data
        ]

        contents.append(
            types.Content(role="user", parts=fn_response_parts)
        )

        follow_up = client.models.generate_content(
            model=model_name,
            contents=contents,
            config=config,
        )
        for part in follow_up.candidates[0].content.parts:
            if part.text:
                text_parts.append(part.text)

    assistant_text = "\n".join(text_parts) if text_parts else ""
    return assistant_text, tool_calls_data


def _stream_gemini(
    conversation_history: list[dict],
    current_requirements: dict | None,
) -> Generator[str, None, tuple[str, list[dict]]]:
    """Gemini streaming: yields text chunks, returns (full_text, tool_calls)."""
    from google.genai import types

    client, config = _build_gemini_config()
    model_name = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    contents = _build_gemini_contents(conversation_history, current_requirements)

    if not contents:
        yield "Bitte sende eine Nachricht."
        return "Bitte sende eine Nachricht.", []

    # Erste Anfrage (non-streaming, um Tool-Calls zu erkennen)
    response = client.models.generate_content(
        model=model_name,
        contents=contents,
        config=config,
    )

    text_parts, tool_calls_data = _parse_gemini_response(response)

    if tool_calls_data and not text_parts:
        # Tool-Calls verarbeiten, dann streamen
        contents.append(response.candidates[0].content)

        fn_response_parts = [
            types.Part.from_function_response(
                name=tc["name"],
                response={"result": {"status": "ok"}},
            )
            for tc in tool_calls_data
        ]

        contents.append(
            types.Content(role="user", parts=fn_response_parts)
        )

        # Follow-Up als Stream
        full_text = ""
        stream = client.models.generate_content_stream(
            model=model_name,
            contents=contents,
            config=config,
        )
        for chunk in stream:
            if chunk.text:
                full_text += chunk.text
                yield chunk.text
        return full_text, tool_calls_data
    elif text_parts:
        # Text war schon in erster Antwort – alles auf einmal (schon da)
        full = "\n".join(text_parts)
        yield full
        return full, tool_calls_data
    else:
        yield ""
        return "", tool_calls_data


# ═══════════════════════════════════════════════════════════════════════════
# Öffentliche API  –  Provider-unabhängig
# ═══════════════════════════════════════════════════════════════════════════

def process_message(
    conversation_history: list[dict],
    current_requirements: dict | None,
) -> tuple[str, list[dict]]:
    """Non-Streaming: gibt (assistant_text, tool_calls_data) zurück."""
    if AI_PROVIDER == "openai":
        return _process_openai(conversation_history, current_requirements)
    elif AI_PROVIDER == "gemini":
        return _process_gemini(conversation_history, current_requirements)
    else:
        raise ValueError(
            f"Unbekannter AI_PROVIDER: '{AI_PROVIDER}'. "
            "Erlaubt: 'openai' oder 'gemini'. Setze AI_PROVIDER in .env."
        )


def process_message_stream(
    conversation_history: list[dict],
    current_requirements: dict | None,
) -> Generator[str, None, tuple[str, list[dict]]]:
    """Streaming: yields text chunks. Die Tool-Calls werden intern verarbeitet.

    Nutzung:
        gen = process_message_stream(history, reqs)
        tool_calls = []
        full_text = ""
        try:
            while True:
                chunk = next(gen)
                full_text += chunk
                # chunk an Client senden …
        except StopIteration as e:
            full_text, tool_calls = e.value
    """
    if AI_PROVIDER == "openai":
        return _stream_openai(conversation_history, current_requirements)
    elif AI_PROVIDER == "gemini":
        return _stream_gemini(conversation_history, current_requirements)
    else:
        raise ValueError(
            f"Unbekannter AI_PROVIDER: '{AI_PROVIDER}'. "
            "Erlaubt: 'openai' oder 'gemini'. Setze AI_PROVIDER in .env."
        )
