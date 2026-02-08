# Agentic Commerce – Backend2

FastAPI-Backend für **Agentic Commerce**: konversationeller Brief, Multi-Händler-Suche (ASOS RapidAPI + 2 Mock-Händler), transparentes Ranking, kombinierter Warenkorb, simulierter Checkout.

## Voraussetzungen

- Python 3.10+
- API-Keys (siehe unten)

## Setup

```bash
cd backend2
cp .env.example .env
# .env bearbeiten: GOOGLE_API_KEY, RAPIDAPI_KEY, RAPIDAPI_ASOS_HOST eintragen
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0
```

- **GOOGLE_API_KEY:** Von [Google AI Studio](https://aistudio.google.com/apikey) (Gemini).
- **RAPIDAPI_KEY / RAPIDAPI_ASOS_HOST:** Von [RapidAPI](https://rapidapi.com/hub) – nach „ASOS“ suchen (z. B. „asos2“), Key und Host aus der API-Beschreibung übernehmen.

## API-Überblick

| Methode | Pfad | Beschreibung |
|--------|------|--------------|
| POST | `/sessions` | Neue Session anlegen |
| GET | `/sessions/{id}` | Session inkl. Chat + Cart |
| POST | `/sessions/{id}/chat` | Nachricht senden (Body: `{"message": "..."}`) |
| POST | `/sessions/{id}/search` | Suche starten (nach Brief-Abschluss) |
| GET | `/sessions/{id}/cart` | Warenkorb abrufen |
| POST | `/sessions/{id}/cart/items` | Produkt in den Warenkorb (Body: AddToCartRequest) |
| DELETE | `/sessions/{id}/cart/items/{item_id}` | Item entfernen |
| PATCH | `/sessions/{id}/cart/items/{item_id}` | Menge ändern (Body: `{"quantity": n}`) |
| POST | `/sessions/{id}/checkout-simulation` | Checkout simulieren |

## Ablauf

1. **Session erstellen** → `POST /sessions`
2. **Chat** → Nutzer beschreibt Wunsch (z. B. „Ski-Outfit, 400€, Größe M, in 5 Tagen“). Agent fragt nach fehlenden Infos und speichert den Brief.
3. **Suche** → `POST /sessions/{id}/search` durchsucht ASOS (RapidAPI) + StyleHub + UrbanOutfit, rankt nach Kosten/Lieferung/Präferenz und liefert „Why is #1 ranked first?“.
4. **Warenkorb** → Frontend legt gewählte Produkte in den Cart (`POST .../cart/items`), Nutzer kann entfernen/mengen ändern.
5. **Checkout** → `POST .../checkout-simulation` zeigt simulierten Ablauf (eine Adresse/Zahlung, Schritte pro Händler).

## Händler

- **ASOS:** Echte Produktdaten über RapidAPI (Host/Key in `.env`).
- **StyleHub / UrbanOutfit:** Mock-Daten im Code (realistische Ski/Party-Artikel).

## Dokumentation

- Swagger: `http://localhost:8000/docs`
- Testseite: `http://localhost:8000/api-test` (falls `api_test.html` vorhanden)
