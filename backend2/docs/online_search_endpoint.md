# KI-Online-Suche (search-online)

## Überblick

Der Endpoint **POST /sessions/{session_id}/search-online** nutzt **Gemini mit Google Search Grounding**, um:

1. **Shops zu wählen**: Die KI entscheidet selbst, welche Online-Shops (z. B. ASOS, Zalando, About You) zum Brief passen.
2. **Im Web zu suchen**: Über das Google-Search-Tool sucht die KI auf diesen Shops nach passenden Produkten.
3. **Zu vergleichen**: Gefundene Produkte werden bewertet; die besten Optionen werden ausgegeben.
4. **Outfits zu strukturieren**: Bei einem Outfit legt die KI fest, aus wie vielen Teilen es besteht (z. B. Oberteil, Hose, Schuhe) und liefert **pro Teil 2 Empfehlungen**.

## Ablauf

- **Phase 1 (Plan)**: Gemini plant ohne Web – Shops + bei Outfit: Teile und Suchbegriffe.
- **Phase 2 (Suche)**: Gemini mit Google Search – sucht pro Outfit-Teil bzw. einmal allgemein nach Produkten.
- **Phase 3 (Vergleich)**: Gemini wählt pro Teil die 2 besten Optionen und formuliert eine kurze Empfehlung.

## Voraussetzungen

- **GOOGLE_API_KEY** in `.env` (wie für den Chat-Agent).
- Modell **Gemini 2.0 Flash** (oder neuer), damit das Tool **Google Search** (Grounding) verfügbar ist. Ohne unterstütztes Tool antwortet die KI aus dem Trainingswissen (kein Live-Web).

## Request

- **Method**: POST  
- **URL**: `/sessions/{session_id}/search-online`  
- **Body**: keiner  
- Session muss im Status **ready_for_search** sein (Brief zuvor per Chat abgeschlossen).

## Response (OnlineSearchResultOut)

| Feld | Beschreibung |
|------|--------------|
| shopping_spec | Der verwendete Brief |
| is_outfit | true, wenn die KI ein mehrteiliges Outfit erkannt hat |
| outfit_parts | Bei Outfit: Liste von Teilen, je mit `part_name` und `options` (2 RankedProductOut) |
| products | Bei Nicht-Outfit: flache Liste der besten Produkte |
| shops_considered | Von der KI gewählte Shops |
| recommendation_text | Kurze Empfehlung der KI |
| search_queries_used | Verwendete Suchanfragen (bei Outfit pro Teil) |

## Beispiel (Outfit)

Nach einem Brief „Ski-Outfit, 400 €, Größe M“ könnte die Antwort u. a. enthalten:

- **is_outfit**: true  
- **outfit_parts**:  
  - part_name: "Jacke", options: [Produkt A, Produkt B]  
  - part_name: "Hose", options: [Produkt C, Produkt D]  
  - part_name: "Schuhe", options: [Produkt E, Produkt F]  
- **recommendation_text**: "Für dein Budget empfehlen wir …"

## Unterschied zur normalen Suche

- **POST …/search**: Nutzt die ASOS-API (und ggf. weitere integrierte Händler), festes Ranking.
- **POST …/search-online**: KI wählt Shops, sucht im Web (Google Search) und vergleicht; bei Outfits 2 Optionen pro Teil.
